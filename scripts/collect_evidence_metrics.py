"""Collect evidence metrics for docs/evidence.md.

Every metric row on docs/evidence.md must carry a generating command, a
commit SHA, and a generation date. This script produces those provenance
fields so evidence.md cannot drift from reality without the drift being
visible.

Usage:
    python scripts/collect_evidence_metrics.py            # write JSON
    python scripts/collect_evidence_metrics.py --verify   # re-run and diff

Output:
    docs/_generated/evidence_metrics.json

Codex condition 2 (bridge/gtkb-start-here-adopter-rewrite-implementation-002.md):
- Every metric row names the source scope, command, commit, and date.
- pytest collection is a deterministic metric; exact equality is enforced.
- Non-deterministic metrics (none currently enumerated) must declare the
  nondeterminism source and the allowed tolerance in code and docs.
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "docs" / "_generated" / "evidence_metrics.json"


@dataclass(frozen=True)
class Metric:
    name: str
    value: Any
    command: str
    source_scope: str
    nondeterminism: str  # "deterministic" or a short explanation.


def _run(cmd: list[str], cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def _head_sha() -> str:
    result = _run(["git", "rev-parse", "--short", "HEAD"])
    return result.stdout.strip() or "unknown"


def _collect_test_count() -> Metric:
    result = _run([sys.executable, "-m", "pytest", "--collect-only", "-q"])
    output = result.stdout + result.stderr
    match = re.search(r"(\d+)\s+tests?\s+collected", output)
    if match:
        value: int | str = int(match.group(1))
    else:
        value = "error: pattern not found in pytest output"
    return Metric(
        name="test_count",
        value=value,
        command="python -m pytest --collect-only -q",
        source_scope="tests/ directory, all collected test ids",
        nondeterminism="deterministic",
    )


def _collect_spec_counts() -> list[Metric]:
    db_path = REPO_ROOT / "groundtruth.db"
    if not db_path.exists():
        return [
            Metric(
                name="specs_by_status",
                value="error: groundtruth.db not found at repo root",
                command="sqlite3 groundtruth.db 'SELECT ...'",
                source_scope="local groundtruth.db",
                nondeterminism="deterministic (at a fixed commit)",
            )
        ]
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.execute(
            "SELECT status, COUNT(*) FROM ("
            "  SELECT id, status FROM specifications"
            "  GROUP BY id HAVING version = MAX(version)"
            ") GROUP BY status ORDER BY status"
        )
        rows = dict(cursor.fetchall())
    finally:
        conn.close()
    return [
        Metric(
            name=f"specs_{status}",
            value=count,
            command="sqlite3 groundtruth.db 'SELECT status, COUNT(*) FROM (...) GROUP BY status'",
            source_scope="local groundtruth-kb/groundtruth.db at repo root",
            nondeterminism="deterministic (at a fixed commit)",
        )
        for status, count in rows.items()
    ]


def _collect_deliberation_count() -> Metric:
    db_path = REPO_ROOT / "groundtruth.db"
    if not db_path.exists():
        return Metric(
            name="deliberations_total",
            value="error: groundtruth.db not found at repo root",
            command="sqlite3 groundtruth.db 'SELECT COUNT(*) FROM deliberations'",
            source_scope="local groundtruth-kb/groundtruth.db at repo root",
            nondeterminism="deterministic (at a fixed commit)",
        )
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.execute("SELECT COUNT(DISTINCT id) FROM deliberations")
        count = cursor.fetchone()[0]
    finally:
        conn.close()
    return Metric(
        name="deliberations_total",
        value=count,
        command="sqlite3 groundtruth.db 'SELECT COUNT(DISTINCT id) FROM deliberations'",
        source_scope=(
            "local groundtruth-kb/groundtruth.db at repo root. "
            "This is the reference install's local archive, NOT the "
            "downstream Agent Red deliberation history which is measured "
            "separately."
        ),
        nondeterminism="deterministic (at a fixed commit)",
    )


def _collect_mypy_strict() -> Metric:
    result = _run([sys.executable, "-m", "mypy", "--strict", "src/groundtruth_kb/"])
    output = result.stdout + result.stderr
    if "Success: no issues found" in output:
        value: dict[str, Any] | str = {
            "status": "pass",
            "source_files": int(re.search(r"found in (\d+) source file", output).group(1))  # type: ignore[union-attr]
            if re.search(r"found in (\d+) source file", output)
            else -1,
        }
    else:
        value = {"status": "fail", "exit_code": result.returncode}
    return Metric(
        name="mypy_strict",
        value=value,
        command="python -m mypy --strict src/groundtruth_kb/",
        source_scope="src/groundtruth_kb/ (all modules)",
        nondeterminism="deterministic",
    )


def _collect_docstring_coverage() -> Metric:
    audit_script = REPO_ROOT / "scripts" / "audit_docstrings.py"
    if not audit_script.exists():
        return Metric(
            name="docstring_coverage",
            value="error: scripts/audit_docstrings.py not found",
            command="python scripts/audit_docstrings.py",
            source_scope="src/groundtruth_kb/ public API",
            nondeterminism="deterministic",
        )
    result = _run([sys.executable, str(audit_script)])
    output = result.stdout + result.stderr
    match = re.search(r"(\d+(?:\.\d+)?)%", output)
    value: float | str = float(match.group(1)) if match else f"error: percentage not found in {output!r}"
    return Metric(
        name="docstring_coverage_percent",
        value=value,
        command="python scripts/audit_docstrings.py",
        source_scope="src/groundtruth_kb/ public API (audit_docstrings.py scope)",
        nondeterminism="deterministic",
    )


def _metric_to_row(metric: Metric, commit_sha: str, timestamp_utc: str) -> dict[str, Any]:
    return {
        "metric_name": metric.name,
        "value": metric.value,
        "command": metric.command,
        "commit_sha": commit_sha,
        "timestamp_utc": timestamp_utc,
        "source_scope": metric.source_scope,
        "nondeterminism": metric.nondeterminism,
    }


def collect() -> dict[str, Any]:
    commit_sha = _head_sha()
    timestamp_utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    metrics: list[Metric] = []
    metrics.append(_collect_test_count())
    metrics.extend(_collect_spec_counts())
    metrics.append(_collect_deliberation_count())
    metrics.append(_collect_mypy_strict())
    metrics.append(_collect_docstring_coverage())

    return {
        "generated_at_utc": timestamp_utc,
        "generated_at_commit": commit_sha,
        "metrics": [_metric_to_row(m, commit_sha, timestamp_utc) for m in metrics],
    }


def write_json(data: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify() -> int:
    if not OUTPUT_PATH.exists():
        print(f"ERROR: {OUTPUT_PATH.relative_to(REPO_ROOT)} does not exist. Run without --verify first.")
        return 2
    stored = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    fresh = collect()

    diffs: list[str] = []
    stored_metrics = {m["metric_name"]: m["value"] for m in stored.get("metrics", [])}
    fresh_metrics = {m["metric_name"]: m["value"] for m in fresh["metrics"]}

    for name, fresh_value in fresh_metrics.items():
        if name not in stored_metrics:
            diffs.append(f"NEW metric: {name}={fresh_value!r}")
            continue
        stored_value = stored_metrics[name]
        if stored_value != fresh_value:
            diffs.append(f"CHANGED: {name} stored={stored_value!r} fresh={fresh_value!r}")
    for name in stored_metrics:
        if name not in fresh_metrics:
            diffs.append(f"REMOVED metric: {name}")

    if diffs:
        print("Evidence drift detected:")
        for line in diffs:
            print(f"  {line}")
        return 1
    print(f"Evidence matches: {len(fresh_metrics)} metrics agree at commit {fresh['generated_at_commit']}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Re-run collector and diff against stored JSON.")
    args = parser.parse_args()

    if args.verify:
        return verify()
    data = collect()
    write_json(data)
    print(f"Wrote {len(data['metrics'])} metrics to {OUTPUT_PATH.relative_to(REPO_ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
