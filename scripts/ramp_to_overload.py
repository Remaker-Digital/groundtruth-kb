"""Ramp-to-overload load test — finds the breaking point per endpoint.

Incrementally increases concurrent users until >5% of requests fail (the
overload threshold). At each step, measures per-endpoint latency (P50, P95,
P99), throughput (RPS), and error rate. Outputs a CSV time series suitable
for charting the degradation curve.

The resulting data shows exactly where rate limiting should be set: the RPM
at which the 95th percentile response time inflects upward or error rate
crosses 5%.

Usage:
    python scripts/ramp_to_overload.py --env staging
    python scripts/ramp_to_overload.py --env staging --max-users 500
    python scripts/ramp_to_overload.py --env staging --step-duration 90

Output:
    tests/performance/ramp-to-overload-{timestamp}.csv   — per-endpoint time series
    tests/performance/ramp-to-overload-{timestamp}.json  — full structured results

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

HOSTS = {
    "staging": "https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
    "production": "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
}

LOCUSTFILE = str(PROJECT_ROOT / "tests" / "performance" / "locustfile.py")
OUTPUT_DIR = PROJECT_ROOT / "tests" / "performance"

# Default ramp steps — each step adds users and measures for step_duration
DEFAULT_STEPS = [10, 25, 50, 75, 100, 150, 200, 250, 300, 400, 500]

# Overload threshold — stop when error rate exceeds this
OVERLOAD_THRESHOLD_PCT = 5.0

# Force UTF-8 stdout on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class EndpointMetrics:
    """Metrics for a single endpoint at a single load step."""
    name: str
    requests: int = 0
    failures: int = 0
    error_rate_pct: float = 0.0
    avg_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    p50: float = 0.0
    p66: float = 0.0
    p75: float = 0.0
    p80: float = 0.0
    p90: float = 0.0
    p95: float = 0.0
    p98: float = 0.0
    p99: float = 0.0
    rps: float = 0.0


@dataclass
class StepResult:
    """Results for an entire load step (all endpoints)."""
    step: int
    users: int
    timestamp: str
    duration_s: float
    total_requests: int = 0
    total_failures: int = 0
    aggregate_error_rate_pct: float = 0.0
    aggregate_p50: float = 0.0
    aggregate_p95: float = 0.0
    aggregate_p99: float = 0.0
    aggregate_rps: float = 0.0
    endpoints: list[EndpointMetrics] = field(default_factory=list)
    overload_reached: bool = False


# ---------------------------------------------------------------------------
# Locust CSV parser
# ---------------------------------------------------------------------------

def _parse_stats_csv(csv_path: Path) -> list[EndpointMetrics]:
    """Parse Locust stats CSV into per-endpoint metrics."""
    metrics = []
    if not csv_path.exists():
        return metrics

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Name", "")
            if not name or name == "Aggregated":
                continue
            req_count = int(_safe_float(row.get("Request Count")))
            fail_count = int(_safe_float(row.get("Failure Count")))
            avg = _safe_float(row.get("Average Response Time"))
            min_rt = _safe_float(row.get("Min Response Time"))
            max_rt = _safe_float(row.get("Max Response Time"))
            rps = _safe_float(row.get("Requests/s"))
            err_pct = (fail_count / req_count * 100) if req_count > 0 else 0.0

            ep = EndpointMetrics(
                name=f"{row.get('Type', 'GET')} {name}",
                requests=req_count,
                failures=fail_count,
                error_rate_pct=round(err_pct, 2),
                avg_ms=round(avg, 1),
                min_ms=round(min_rt, 1),
                max_ms=round(max_rt, 1),
                p50=_safe_float(row.get("50%")),
                p66=_safe_float(row.get("66%")),
                p75=_safe_float(row.get("75%")),
                p80=_safe_float(row.get("80%")),
                p90=_safe_float(row.get("90%")),
                p95=_safe_float(row.get("95%")),
                p98=_safe_float(row.get("98%")),
                p99=_safe_float(row.get("99%")),
                rps=round(rps, 2),
            )
            metrics.append(ep)
    return metrics


def _safe_float(value: Any, default: float = 0.0) -> float:
    """Convert a CSV value to float, handling N/A and empty strings."""
    if value is None or value == "" or value == "N/A":
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _parse_percentiles_csv(csv_path: Path, metrics: list[EndpointMetrics]) -> None:
    """Enrich endpoint metrics with percentile data from Locust stats_history CSV."""
    if not csv_path.exists():
        return

    # Build lookup by name
    by_name: dict[str, EndpointMetrics] = {}
    for m in metrics:
        # Strip method prefix for matching
        short = m.name.split(" ", 1)[-1] if " " in m.name else m.name
        by_name[short] = m
        by_name[m.name] = m

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Name", "")
            if not name or name == "Aggregated":
                continue
            ep = by_name.get(name)
            if not ep:
                continue
            ep.p50 = _safe_float(row.get("50%"))
            ep.p66 = _safe_float(row.get("66%"))
            ep.p75 = _safe_float(row.get("75%"))
            ep.p80 = _safe_float(row.get("80%"))
            ep.p90 = _safe_float(row.get("90%"))
            ep.p95 = _safe_float(row.get("95%"))
            ep.p98 = _safe_float(row.get("98%"))
            ep.p99 = _safe_float(row.get("99%"))


def _parse_aggregate(csv_path: Path) -> dict[str, Any]:
    """Parse the Aggregated row from Locust stats CSV (includes percentiles)."""
    if not csv_path.exists():
        return {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Name") == "Aggregated":
                return {
                    "requests": int(_safe_float(row.get("Request Count"))),
                    "failures": int(_safe_float(row.get("Failure Count"))),
                    "avg_ms": _safe_float(row.get("Average Response Time")),
                    "rps": _safe_float(row.get("Requests/s")),
                    "p50": _safe_float(row.get("50%")),
                    "p95": _safe_float(row.get("95%")),
                    "p99": _safe_float(row.get("99%")),
                }
    return {}


def _parse_aggregate_percentiles(csv_path: Path) -> dict[str, float]:
    """Parse percentiles for the Aggregated row."""
    if not csv_path.exists():
        return {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("Name") == "Aggregated":
                return {
                    "p50": _safe_float(row.get("50%")),
                    "p95": _safe_float(row.get("95%")),
                    "p99": _safe_float(row.get("99%")),
                }
    return {}


# ---------------------------------------------------------------------------
# Single step runner
# ---------------------------------------------------------------------------

def _run_step(
    step_num: int,
    users: int,
    host: str,
    duration_s: int,
    spawn_rate: int,
    env_vars: dict[str, str],
) -> StepResult:
    """Run a single load step with the given user count."""
    ts = datetime.now(timezone.utc).isoformat()
    print(f"\n{'='*70}")
    print(f"  Step {step_num}: {users} concurrent users for {duration_s}s")
    print(f"{'='*70}")

    # Temp CSV prefix for this step
    csv_prefix = str(OUTPUT_DIR / f"_ramp_step_{step_num}")

    cmd = [
        sys.executable, "-m", "locust",
        "-f", LOCUSTFILE,
        "--host", host,
        "--headless",
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", f"{duration_s}s",
        "--csv", csv_prefix,
        "--only-summary",
        "--loglevel", "WARNING",
    ]

    env = {**os.environ, **env_vars}

    t0 = time.time()
    try:
        r = subprocess.run(
            cmd, cwd=str(PROJECT_ROOT), env=env,
            capture_output=True, text=True,
            timeout=duration_s + 60,  # grace period
        )
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] Step {step_num} timed out after {duration_s + 60}s")
        return StepResult(
            step=step_num, users=users, timestamp=ts,
            duration_s=time.time() - t0, overload_reached=True,
        )
    dt = time.time() - t0

    # Parse CSV results — stats.csv has everything including percentiles
    stats_csv = Path(f"{csv_prefix}_stats.csv")

    endpoints = _parse_stats_csv(stats_csv)
    agg = _parse_aggregate(stats_csv)

    total_req = agg.get("requests", 0)
    total_fail = agg.get("failures", 0)
    err_rate = (total_fail / total_req * 100) if total_req > 0 else 0.0

    result = StepResult(
        step=step_num,
        users=users,
        timestamp=ts,
        duration_s=round(dt, 1),
        total_requests=total_req,
        total_failures=total_fail,
        aggregate_error_rate_pct=round(err_rate, 2),
        aggregate_p50=agg.get("p50", 0),
        aggregate_p95=agg.get("p95", 0),
        aggregate_p99=agg.get("p99", 0),
        aggregate_rps=round(agg.get("rps", 0), 2),
        endpoints=endpoints,
        overload_reached=err_rate > OVERLOAD_THRESHOLD_PCT,
    )

    # Print step summary
    print(f"  Requests: {total_req}  Failures: {total_fail}  "
          f"Error: {err_rate:.1f}%  RPS: {result.aggregate_rps}")
    print(f"  P50: {result.aggregate_p50}ms  P95: {result.aggregate_p95}ms  "
          f"P99: {result.aggregate_p99}ms")

    if endpoints:
        print(f"\n  {'Endpoint':<55} {'Reqs':>5} {'Fail':>5} {'Err%':>6} "
              f"{'P50':>6} {'P95':>6} {'P99':>6} {'RPS':>6}")
        print(f"  {'-'*55} {'-'*5} {'-'*5} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")
        for ep in sorted(endpoints, key=lambda e: e.name):
            print(f"  {ep.name:<55} {ep.requests:>5} {ep.failures:>5} "
                  f"{ep.error_rate_pct:>5.1f}% {ep.p50:>6.0f} {ep.p95:>6.0f} "
                  f"{ep.p99:>6.0f} {ep.rps:>6.2f}")

    if result.overload_reached:
        print(f"\n  ** OVERLOAD THRESHOLD REACHED: {err_rate:.1f}% > {OVERLOAD_THRESHOLD_PCT}% **")

    # Cleanup temp CSVs
    for suffix in ["_stats.csv", "_stats_history.csv", "_failures.csv",
                    "_exceptions.csv"]:
        p = Path(f"{csv_prefix}{suffix}")
        if p.exists():
            p.unlink()

    return result


# ---------------------------------------------------------------------------
# Write output files
# ---------------------------------------------------------------------------

def _write_time_series_csv(results: list[StepResult], path: Path) -> None:
    """Write per-endpoint time series CSV for charting."""
    rows: list[dict[str, Any]] = []

    for step in results:
        base = {
            "step": step.step,
            "users": step.users,
            "timestamp": step.timestamp,
            "total_requests": step.total_requests,
            "total_failures": step.total_failures,
            "aggregate_error_pct": step.aggregate_error_rate_pct,
            "aggregate_p50": step.aggregate_p50,
            "aggregate_p95": step.aggregate_p95,
            "aggregate_p99": step.aggregate_p99,
            "aggregate_rps": step.aggregate_rps,
        }
        if step.endpoints:
            for ep in step.endpoints:
                rows.append({
                    **base,
                    "endpoint": ep.name,
                    "ep_requests": ep.requests,
                    "ep_failures": ep.failures,
                    "ep_error_pct": ep.error_rate_pct,
                    "ep_avg_ms": ep.avg_ms,
                    "ep_p50": ep.p50,
                    "ep_p66": ep.p66,
                    "ep_p75": ep.p75,
                    "ep_p80": ep.p80,
                    "ep_p90": ep.p90,
                    "ep_p95": ep.p95,
                    "ep_p98": ep.p98,
                    "ep_p99": ep.p99,
                    "ep_rps": ep.rps,
                })
        else:
            rows.append({**base, "endpoint": "AGGREGATE"})

    if not rows:
        return

    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_json(results: list[StepResult], path: Path) -> None:
    """Write full structured results as JSON."""
    data = {
        "test": "ramp-to-overload",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "overload_threshold_pct": OVERLOAD_THRESHOLD_PCT,
        "steps": [asdict(r) for r in results],
        "summary": {
            "total_steps": len(results),
            "max_users_before_overload": max(
                (r.users for r in results if not r.overload_reached), default=0
            ),
            "overload_users": next(
                (r.users for r in results if r.overload_reached), None
            ),
            "peak_rps": max((r.aggregate_rps for r in results), default=0),
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Warmup
# ---------------------------------------------------------------------------

def _warmup(host: str) -> None:
    """Send health requests to wake up cold-start containers."""
    import urllib.request
    import ssl

    ctx = ssl.create_default_context()
    url = f"{host}/health"
    print(f"Warming up: {url}")
    for attempt in range(5):
        try:
            req = urllib.request.Request(url)
            resp = urllib.request.urlopen(req, timeout=30, context=ctx)
            print(f"  Attempt {attempt+1}: HTTP {resp.status}")
            if resp.status == 200:
                return
        except Exception as e:
            print(f"  Attempt {attempt+1}: {e}")
            if attempt < 4:
                time.sleep(10)
    print("  Warning: warmup incomplete, proceeding anyway")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Ramp-to-overload load test")
    parser.add_argument("--env", choices=["staging", "production"], default="staging")
    parser.add_argument("--host", help="Override host URL")
    parser.add_argument("--max-users", type=int, default=500,
                        help="Maximum users to ramp to (default: 500)")
    parser.add_argument("--step-duration", type=int, default=60,
                        help="Seconds per step (default: 60)")
    parser.add_argument("--spawn-rate", type=int, default=10,
                        help="Users spawned per second (default: 10)")
    parser.add_argument("--cooldown", type=int, default=15,
                        help="Seconds between steps (default: 15)")
    args = parser.parse_args()

    host = args.host or HOSTS[args.env]
    steps = [s for s in DEFAULT_STEPS if s <= args.max_users]
    if not steps:
        steps = [args.max_users]

    # Load env vars for auth
    sys.path.insert(0, str(PROJECT_ROOT))
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    try:
        from scripts._env import load_env_local
        load_env_local()
    except ImportError:
        pass

    env_vars: dict[str, str] = {}
    # Try multiple env var names — .env.local uses STAGING_REMAKER_* format
    api_key = (os.environ.get("STAGING_REMAKER_USER_KEY")
               or os.environ.get("STAGING_REMAKER_DIGITAL_001_SUPERADMIN_KEY", ""))
    widget_key = (os.environ.get("STAGING_REMAKER_WIDGET_KEY")
                  or os.environ.get("STAGING_REMAKER_DIGITAL_001_WIDGET_KEY", ""))
    if api_key:
        env_vars["LOAD_TEST_API_KEY"] = api_key
    if widget_key:
        env_vars["LOAD_TEST_WIDGET_KEY"] = widget_key
    print(f"  API key: {api_key[:12]}..." if api_key else "  API key: NOT SET")
    print(f"  Widget key: {widget_key[:15]}..." if widget_key else "  Widget key: NOT SET")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    csv_path = OUTPUT_DIR / f"ramp-to-overload-{timestamp}.csv"
    json_path = OUTPUT_DIR / f"ramp-to-overload-{timestamp}.json"

    print(f"Ramp-to-overload load test")
    print(f"  Host: {host}")
    print(f"  Steps: {steps}")
    print(f"  Duration per step: {args.step_duration}s")
    print(f"  Overload threshold: {OVERLOAD_THRESHOLD_PCT}%")
    print(f"  Output: {csv_path.name}")

    # Warmup
    _warmup(host)

    results: list[StepResult] = []
    for i, user_count in enumerate(steps, 1):
        result = _run_step(
            step_num=i,
            users=user_count,
            host=host,
            duration_s=args.step_duration,
            spawn_rate=args.spawn_rate,
            env_vars=env_vars,
        )
        results.append(result)

        # Write intermediate results after each step (crash resilience)
        _write_time_series_csv(results, csv_path)
        _write_json(results, json_path)

        if result.overload_reached:
            print(f"\nOverload reached at {user_count} users. Stopping ramp.")
            break

        # Cooldown between steps
        if i < len(steps):
            print(f"\n  Cooling down {args.cooldown}s before next step...")
            time.sleep(args.cooldown)

    # Final summary
    print(f"\n{'='*70}")
    print(f"  RAMP-TO-OVERLOAD SUMMARY")
    print(f"{'='*70}")
    print(f"\n  {'Step':>4} {'Users':>6} {'Reqs':>6} {'Fail':>5} {'Err%':>6} "
          f"{'P50':>6} {'P95':>6} {'P99':>6} {'RPS':>6}")
    print(f"  {'-'*4} {'-'*6} {'-'*6} {'-'*5} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")

    for r in results:
        marker = " ** OVERLOAD" if r.overload_reached else ""
        print(f"  {r.step:>4} {r.users:>6} {r.total_requests:>6} "
              f"{r.total_failures:>5} {r.aggregate_error_rate_pct:>5.1f}% "
              f"{r.aggregate_p50:>6.0f} {r.aggregate_p95:>6.0f} "
              f"{r.aggregate_p99:>6.0f} {r.aggregate_rps:>6.1f}{marker}")

    max_safe = max((r.users for r in results if not r.overload_reached), default=0)
    overload_at = next((r.users for r in results if r.overload_reached), None)
    peak_rps = max((r.aggregate_rps for r in results), default=0)

    print(f"\n  Max safe users: {max_safe}")
    if overload_at:
        print(f"  Overload at: {overload_at} users")
    else:
        print(f"  Overload NOT reached (max tested: {steps[-1]} users)")
    print(f"  Peak RPS: {peak_rps:.1f}")
    print(f"  Recommended RPM ceiling: {int(peak_rps * 60 * 0.8)} "
          f"(80% of peak {peak_rps:.1f} RPS = {peak_rps * 60:.0f} RPM)")
    print(f"\n  CSV: {csv_path}")
    print(f"  JSON: {json_path}")


if __name__ == "__main__":
    main()
