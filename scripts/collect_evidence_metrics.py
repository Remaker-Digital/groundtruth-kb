"""Collect evidence metrics for docs/evidence.md.

Every metric row on docs/evidence.md must carry a generating command, a
commit SHA, and a generation date. This script produces those provenance
fields so evidence.md cannot drift from reality without the drift being
visible.

Metrics are partitioned into two classes:

    gate_bound   — deterministic at a fixed commit, compared by --verify.
                   (test_count, mypy_strict, docstring_coverage_percent)
    live_snapshot — DB-backed counts from the gitignored local groundtruth.db.
                   Regenerated on every run, NOT compared by --verify
                   because the DB is mutable and a fresh `gt project init`
                   produces different values.
                   (specs_specified, specs_verified, deliberations_total)

Usage:
    python scripts/collect_evidence_metrics.py            # write JSON
    python scripts/collect_evidence_metrics.py --verify   # re-run and diff

Output:
    docs/_generated/evidence_metrics.json

Provenance contract for --verify (Codex condition P1-2 of
bridge/gtkb-start-here-adopter-rewrite-implementation-006.md):

- `docs/evidence.md` must be an exact render of the committed JSON.
- Each gate-bound metric's `commit_sha` must agree with the JSON-level
  `generated_at_commit`.
- For every gate-bound metric, the fresh run must match the stored row on
  `metric_name`, `value`, `command`, `source_scope`, and `nondeterminism`.
- `commit_sha` and `timestamp_utc` are intentionally NOT compared against
  the fresh run — they are re-stamped by design — but their internal
  consistency (per-metric `commit_sha` == top-level `generated_at_commit`)
  IS enforced on the STORED JSON.
- `live_snapshot` values are NOT compared against the fresh run. Schema
  sanity (required fields present, `reproducibility: local_install_snapshot`
  tag present) IS enforced.
- `docs/evidence.md` is re-rendered from the *committed* JSON into a temp
  path and diffed line-by-line against the committed markdown. Divergence
  fails the gate.
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import json
import re
import sqlite3
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = REPO_ROOT / "docs" / "_generated" / "evidence_metrics.json"
EVIDENCE_MD_PATH = REPO_ROOT / "docs" / "evidence.md"

# Field set compared across fresh vs. stored for every gate-bound metric.
# Excludes commit_sha and timestamp_utc (re-stamped every run) per the
# provenance contract documented in the module docstring above.
GATE_COMPARE_FIELDS: tuple[str, ...] = (
    "metric_name",
    "value",
    "command",
    "source_scope",
    "nondeterminism",
)

# Fields required on every live_snapshot row for schema sanity.
LIVE_REQUIRED_FIELDS: tuple[str, ...] = (
    "metric_name",
    "value",
    "command",
    "source_scope",
    "commit_sha",
    "timestamp_utc",
    "reproducibility",
)


@dataclass(frozen=True)
class Metric:
    name: str
    value: Any
    command: str
    source_scope: str
    nondeterminism: str  # "deterministic" or a short explanation.


@dataclass(frozen=True)
class LiveMetric:
    name: str
    value: Any
    command: str
    source_scope: str
    # Reproducibility class — always "local_install_snapshot" for DB metrics.
    reproducibility: str = "local_install_snapshot"


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


# ---------------------------------------------------------------------------
# Gate-bound collectors — deterministic at a fixed commit
# ---------------------------------------------------------------------------


def _collect_test_count() -> Metric:
    result = _run([sys.executable, "-m", "pytest", "--collect-only", "-q"])
    output = result.stdout + result.stderr
    match = re.search(r"(\d+)\s+tests?\s+collected", output)
    value: int | str = int(match.group(1)) if match else "error: pattern not found in pytest output"
    return Metric(
        name="test_count",
        value=value,
        command="python -m pytest --collect-only -q",
        source_scope="tests/ directory, all collected test ids",
        nondeterminism="deterministic",
    )


def _collect_mypy_strict() -> Metric:
    result = _run([sys.executable, "-m", "mypy", "--strict", "src/groundtruth_kb/"])
    output = result.stdout + result.stderr
    value: dict[str, Any] | str
    if "Success: no issues found" in output:
        count_match = re.search(r"found in (\d+) source file", output)
        value = {
            "status": "pass",
            "source_files": int(count_match.group(1)) if count_match else -1,
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
            name="docstring_coverage_percent",
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


# ---------------------------------------------------------------------------
# Live-snapshot collectors — DB-backed, non-reproducible across machines
# ---------------------------------------------------------------------------


def _collect_spec_counts() -> list[LiveMetric]:
    db_path = REPO_ROOT / "groundtruth.db"
    if not db_path.exists():
        return [
            LiveMetric(
                name="specs_error",
                value="error: groundtruth.db not found at repo root",
                command="sqlite3 groundtruth.db 'SELECT ...'",
                source_scope="local groundtruth.db",
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
        LiveMetric(
            name=f"specs_{status}",
            value=count,
            command="sqlite3 groundtruth.db 'SELECT status, COUNT(*) FROM (...) GROUP BY status'",
            source_scope="local groundtruth-kb/groundtruth.db at repo root",
        )
        for status, count in rows.items()
    ]


def _collect_deliberation_count() -> LiveMetric:
    db_path = REPO_ROOT / "groundtruth.db"
    if not db_path.exists():
        return LiveMetric(
            name="deliberations_total",
            value="error: groundtruth.db not found at repo root",
            command="sqlite3 groundtruth.db 'SELECT COUNT(*) FROM deliberations'",
            source_scope="local groundtruth-kb/groundtruth.db at repo root",
        )
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.execute("SELECT COUNT(DISTINCT id) FROM deliberations")
        count = cursor.fetchone()[0]
    finally:
        conn.close()
    return LiveMetric(
        name="deliberations_total",
        value=count,
        command="sqlite3 groundtruth.db 'SELECT COUNT(DISTINCT id) FROM deliberations'",
        source_scope=(
            "local groundtruth-kb/groundtruth.db at repo root. "
            "This is the reference install's local archive, NOT the "
            "downstream Agent Red deliberation history which is measured "
            "separately."
        ),
    )


# ---------------------------------------------------------------------------
# Serialization helpers
# ---------------------------------------------------------------------------


def _gate_to_row(metric: Metric, commit_sha: str, timestamp_utc: str) -> dict[str, Any]:
    return {
        "metric_name": metric.name,
        "value": metric.value,
        "command": metric.command,
        "commit_sha": commit_sha,
        "timestamp_utc": timestamp_utc,
        "source_scope": metric.source_scope,
        "nondeterminism": metric.nondeterminism,
    }


def _live_to_row(metric: LiveMetric, commit_sha: str, timestamp_utc: str) -> dict[str, Any]:
    return {
        "metric_name": metric.name,
        "value": metric.value,
        "command": metric.command,
        "commit_sha": commit_sha,
        "timestamp_utc": timestamp_utc,
        "source_scope": metric.source_scope,
        "reproducibility": metric.reproducibility,
    }


def collect() -> dict[str, Any]:
    commit_sha = _head_sha()
    timestamp_utc = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    gate_metrics: list[Metric] = [
        _collect_test_count(),
        _collect_mypy_strict(),
        _collect_docstring_coverage(),
    ]
    live_metrics: list[LiveMetric] = []
    live_metrics.extend(_collect_spec_counts())
    live_metrics.append(_collect_deliberation_count())

    return {
        "generated_at_utc": timestamp_utc,
        "generated_at_commit": commit_sha,
        "gate_bound": [_gate_to_row(m, commit_sha, timestamp_utc) for m in gate_metrics],
        "live_snapshot": [_live_to_row(m, commit_sha, timestamp_utc) for m in live_metrics],
    }


def write_json(data: dict[str, Any]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# --verify implementation
# ---------------------------------------------------------------------------


@dataclass
class VerifyReport:
    diffs: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.diffs

    def add(self, msg: str) -> None:
        self.diffs.append(msg)


def _compare_gate_bound(stored: list[dict[str, Any]], fresh: list[dict[str, Any]], report: VerifyReport) -> None:
    stored_by_name = {m["metric_name"]: m for m in stored}
    fresh_by_name = {m["metric_name"]: m for m in fresh}

    for name, fresh_row in fresh_by_name.items():
        if name not in stored_by_name:
            report.add(f"NEW gate-bound metric not in stored JSON: {name}={fresh_row.get('value')!r}")
            continue
        stored_row = stored_by_name[name]
        for field_name in GATE_COMPARE_FIELDS:
            stored_val = stored_row.get(field_name)
            fresh_val = fresh_row.get(field_name)
            if stored_val != fresh_val:
                report.add(
                    f"GATE-BOUND FIELD MISMATCH: metric={name} field={field_name} "
                    f"stored={stored_val!r} fresh={fresh_val!r}"
                )
    for name in stored_by_name:
        if name not in fresh_by_name:
            report.add(f"REMOVED gate-bound metric: {name}")


def _check_gate_commit_consistency(data: dict[str, Any], report: VerifyReport) -> None:
    top_commit = data.get("generated_at_commit")
    for m in data.get("gate_bound", []):
        per_metric_commit = m.get("commit_sha")
        if per_metric_commit != top_commit:
            report.add(
                f"GATE-BOUND COMMIT DRIFT: metric={m.get('metric_name')} "
                f"commit_sha={per_metric_commit!r} != generated_at_commit={top_commit!r}"
            )


def _check_live_schema(data: dict[str, Any], report: VerifyReport) -> None:
    top_commit = data.get("generated_at_commit")
    for m in data.get("live_snapshot", []):
        for required in LIVE_REQUIRED_FIELDS:
            if required not in m:
                report.add(f"LIVE-SNAPSHOT SCHEMA: metric={m.get('metric_name')!r} missing required field {required!r}")
        # Reproducibility tag must be explicit.
        repro = m.get("reproducibility")
        if repro != "local_install_snapshot":
            report.add(
                f"LIVE-SNAPSHOT SCHEMA: metric={m.get('metric_name')!r} "
                f"reproducibility={repro!r} must be 'local_install_snapshot'"
            )
        # Live metrics carry the same commit SHA as the top-level (they are
        # stamped at the same run) — drift here means the stored JSON was
        # hand-edited or concatenated across runs.
        live_commit = m.get("commit_sha")
        if live_commit != top_commit:
            report.add(
                f"LIVE-SNAPSHOT COMMIT DRIFT: metric={m.get('metric_name')} "
                f"commit_sha={live_commit!r} != generated_at_commit={top_commit!r}"
            )


def _check_markdown_consistency(report: VerifyReport) -> None:
    """Re-render docs/evidence.md from the *committed* JSON and diff.

    Uses the committed JSON (not the fresh run) so that a mutable local
    groundtruth.db cannot flap the gate. A fresh render from the committed
    JSON is always byte-identical to the committed markdown when the two
    are in sync.
    """
    if not EVIDENCE_MD_PATH.exists():
        report.add(f"MARKDOWN MISSING: {EVIDENCE_MD_PATH.relative_to(REPO_ROOT)} does not exist.")
        return

    # Import lazily so that verify() does not hard-require the renderer
    # for its early checks.
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        import render_evidence_md  # type: ignore[import-not-found]
    finally:
        sys.path.pop(0)

    try:
        data = render_evidence_md.load_json(OUTPUT_PATH)
        fresh_md = render_evidence_md.render(data)
    except (FileNotFoundError, ValueError) as exc:
        report.add(f"RENDER FAILED: {exc}")
        return

    committed_md = EVIDENCE_MD_PATH.read_text(encoding="utf-8")
    if fresh_md == committed_md:
        return

    # Surface a line-level diff in the report so the developer sees exactly
    # what diverged.
    diff_lines = list(
        difflib.unified_diff(
            committed_md.splitlines(keepends=True),
            fresh_md.splitlines(keepends=True),
            fromfile="committed: docs/evidence.md",
            tofile="rendered from committed JSON",
            n=2,
        )
    )
    report.add(
        "MARKDOWN DRIFT: docs/evidence.md does not match a fresh render of "
        "the committed JSON. Re-run `python scripts/render_evidence_md.py`."
    )
    for line in diff_lines[:40]:
        # Truncate extremely wide lines so terminal output stays readable.
        report.add(f"  {line.rstrip()[:240]}")
    if len(diff_lines) > 40:
        report.add(f"  ... ({len(diff_lines) - 40} more diff lines)")

    # Also write the fresh render to a temp file for inspection.
    with tempfile.NamedTemporaryFile(
        "w", delete=False, suffix=".md", encoding="utf-8", prefix="evidence-verify-"
    ) as fh:
        fh.write(fresh_md)
        report.add(f"  full fresh render written to: {fh.name}")


def verify() -> int:
    if not OUTPUT_PATH.exists():
        print(f"ERROR: {OUTPUT_PATH.relative_to(REPO_ROOT)} does not exist. Run without --verify first.")
        return 2
    try:
        stored = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: {OUTPUT_PATH.relative_to(REPO_ROOT)} is not valid JSON: {exc}")
        return 2

    if "gate_bound" not in stored or "live_snapshot" not in stored:
        print(
            "ERROR: stored evidence_metrics.json is from the legacy schema "
            "(missing gate_bound/live_snapshot arrays). Re-run without --verify "
            "to migrate."
        )
        return 2

    report = VerifyReport()
    _check_gate_commit_consistency(stored, report)
    _check_live_schema(stored, report)

    fresh = collect()
    _compare_gate_bound(stored.get("gate_bound", []), fresh["gate_bound"], report)
    _check_markdown_consistency(report)

    if report.diffs:
        print("Evidence drift detected:")
        for line in report.diffs:
            print(f"  {line}")
        # Informational print: live_snapshot values were regenerated but not
        # compared — surface them so the developer knows what they look like
        # on this machine.
        print()
        print("INFO: live_snapshot values were regenerated (not compared):")
        for m in fresh.get("live_snapshot", []):
            print(f"  {m['metric_name']} = {m['value']!r}  ({m['source_scope']})")
        return 1

    print(
        f"Evidence matches: {len(fresh['gate_bound'])} gate-bound metrics agree at commit "
        f"{fresh['generated_at_commit']}; docs/evidence.md matches a fresh render of the "
        "committed JSON."
    )
    print()
    print("INFO: live_snapshot values were regenerated (not compared):")
    for m in fresh.get("live_snapshot", []):
        print(f"  {m['metric_name']} = {m['value']!r}  ({m['source_scope']})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Re-run collector and diff against stored JSON.")
    args = parser.parse_args()

    if args.verify:
        return verify()
    data = collect()
    write_json(data)
    print(
        f"Wrote {len(data['gate_bound'])} gate-bound and {len(data['live_snapshot'])} live-snapshot metrics "
        f"to {OUTPUT_PATH.relative_to(REPO_ROOT)}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
