#!/usr/bin/env python3
"""
Project Integrity Scan — Drift, Loss & Inefficiency Audit

5-track audit tool for the Agent Red Customer Experience project:
  Track 1: KB Referential Integrity (offline)
  Track 2: Assertion Validity Audit (offline)
  Track 3: Configuration Drift Detection (live API)
  Track 4: Source File Consistency (offline)
  Track 5: Process Efficiency Metrics (offline)

Usage:
  python scripts/integrity_scan.py                    # All tracks (offline only)
  python scripts/integrity_scan.py --live              # All tracks including live API
  python scripts/integrity_scan.py --track 1 2         # Specific tracks only
  python scripts/integrity_scan.py --json              # JSON output to integrity-results/

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
KB_DIR = PROJECT_ROOT / "tools" / "knowledge-db"
RESULTS_DIR = SCRIPT_DIR / "integrity-results"

sys.path.insert(0, str(KB_DIR))
from db import KnowledgeDB  # noqa: E402


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _print_header(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def _print_check(name: str, status: str, count: int, details: list[str] | None = None) -> None:
    icon = "PASS" if status == "pass" else "FIND" if status == "finding" else "SKIP"
    print(f"  [{icon}] {name}: {count}")
    if details:
        for d in details[:10]:
            print(f"         {d}")
        if len(details) > 10:
            print(f"         ... and {len(details) - 10} more")


# ===================================================================
# TRACK 1: KB Referential Integrity
# ===================================================================


def track_1_kb_integrity(db: KnowledgeDB) -> dict:
    """Check referential integrity across KB tables."""
    _print_header("Track 1: KB Referential Integrity")
    conn = db._get_conn()
    findings = {}

    # 1a. Orphaned test artifacts — tests referencing non-existent specs
    orphaned_tests = conn.execute("""
        SELECT t.id, t.spec_id, t.title
        FROM current_tests t
        LEFT JOIN current_specifications s ON t.spec_id = s.id
        WHERE s.id IS NULL
    """).fetchall()
    ids = [f"{r['id']} -> {r['spec_id']}" for r in orphaned_tests]
    findings["orphaned_tests"] = {"count": len(ids), "ids": ids}
    _print_check("Orphaned test artifacts (spec_id not in specs)", "finding" if ids else "pass", len(ids), ids)

    # 1b. Orphaned work items — WIs referencing non-existent specs
    orphaned_wis = conn.execute("""
        SELECT w.id, w.source_spec_id, w.title
        FROM current_work_items w
        LEFT JOIN current_specifications s ON w.source_spec_id = s.id
        WHERE w.source_spec_id IS NOT NULL AND w.source_spec_id != '' AND s.id IS NULL
    """).fetchall()
    ids = [f"{r['id']} -> {r['source_spec_id']}" for r in orphaned_wis]
    findings["orphaned_work_items"] = {"count": len(ids), "ids": ids}
    _print_check("Orphaned work items (source_spec_id not in specs)", "finding" if ids else "pass", len(ids), ids)

    # 1c. Orphaned test_coverage — coverage links to non-existent specs
    orphaned_cov = conn.execute("""
        SELECT tc.spec_id, tc.test_file, tc.test_function
        FROM test_coverage tc
        LEFT JOIN current_specifications s ON tc.spec_id = s.id
        WHERE s.id IS NULL
    """).fetchall()
    ids = list({r["spec_id"] for r in orphaned_cov})
    findings["orphaned_test_coverage"] = {"count": len(ids), "spec_ids": ids}
    _print_check("Orphaned test_coverage (spec_id not in specs)", "finding" if ids else "pass", len(ids), ids)

    # 1d. Tests referencing retired specs (not orphaned, but wasteful)
    retired_spec_tests = conn.execute("""
        SELECT t.id, t.spec_id, s.status
        FROM current_tests t
        JOIN current_specifications s ON t.spec_id = s.id
        WHERE s.status = 'retired'
    """).fetchall()
    ids = list({r["spec_id"] for r in retired_spec_tests})
    findings["tests_on_retired_specs"] = {
        "count": len(retired_spec_tests),
        "unique_specs": len(ids),
        "spec_ids": ids,
    }
    _print_check(
        "Test artifacts linked to retired specs",
        "finding" if ids else "pass",
        len(retired_spec_tests),
        [f"{len(retired_spec_tests)} tests across {len(ids)} retired specs"],
    )

    # 1e. Work items open >60 days
    stale_wis = conn.execute("""
        SELECT id, title, changed_at, resolution_status
        FROM current_work_items
        WHERE resolution_status = 'open'
          AND julianday('now') - julianday(changed_at) > 60
        ORDER BY changed_at ASC
    """).fetchall()
    ids = [f"{r['id']} ({r['changed_at'][:10]}): {r['title'][:60]}" for r in stale_wis]
    findings["stale_work_items"] = {"count": len(ids), "items": ids}
    _print_check("Work items open >60 days", "finding" if ids else "pass", len(ids), ids)

    # 1f. Test artifacts never executed
    never_executed = conn.execute("""
        SELECT COUNT(*) as cnt FROM current_tests
        WHERE last_result IS NULL AND last_executed_at IS NULL
    """).fetchone()["cnt"]
    total_tests = conn.execute("SELECT COUNT(*) FROM current_tests").fetchone()[0]
    findings["never_executed_tests"] = {
        "count": never_executed,
        "total": total_tests,
        "pct": round(never_executed / total_tests * 100, 1) if total_tests else 0,
    }
    _print_check(
        "Test artifacts never executed",
        "finding" if never_executed > 0 else "pass",
        never_executed,
        [f"{never_executed}/{total_tests} ({findings['never_executed_tests']['pct']}%)"],
    )

    return findings


# ===================================================================
# TRACK 2: Assertion Validity Audit
# ===================================================================


def track_2_assertion_validity(db: KnowledgeDB) -> dict:
    """Validate that assertions reference real, matching code."""
    _print_header("Track 2: Assertion Validity Audit")
    conn = db._get_conn()
    findings = {}

    # Get all specs with assertions
    specs_with_assertions = conn.execute("""
        SELECT id, status, assertions FROM current_specifications
        WHERE assertions IS NOT NULL AND assertions != 'null' AND assertions != '[]'
    """).fetchall()

    stale_files = []  # assertion file doesn't exist
    dead_patterns = []  # file exists but pattern not found
    overly_broad = []  # pattern matches >50 times
    duplicate_pairs = {}  # (file, pattern) -> [spec_ids]
    retired_with_assertions = []  # retired specs still carrying assertions

    for spec in specs_with_assertions:
        spec_id = spec["id"]
        status = spec["status"]
        try:
            assertions = json.loads(spec["assertions"])
        except (json.JSONDecodeError, TypeError):
            continue

        if not isinstance(assertions, list):
            continue

        if status == "retired":
            retired_with_assertions.append(spec_id)

        for a in assertions:
            a_type = a.get("type", "grep")
            a_file = a.get("file", "")
            a_pattern = a.get("pattern", "")

            if a_type not in ("grep", "grep_absent", "glob"):
                continue
            if not a_file or not a_pattern:
                continue

            full_path = PROJECT_ROOT / a_file
            pair_key = (a_file, a_pattern)

            # Track duplicates
            duplicate_pairs.setdefault(pair_key, []).append(spec_id)

            if a_type == "glob":
                continue  # glob checks file existence, not content

            if not full_path.exists():
                stale_files.append(f"SPEC-{spec_id}: {a_file}")
                continue

            # Check if pattern matches
            if a_type == "grep":
                try:
                    content = full_path.read_text(encoding="utf-8", errors="replace")
                    match_count = len(re.findall(re.escape(a_pattern), content))
                    if match_count == 0:
                        dead_patterns.append(f"SPEC-{spec_id}: '{a_pattern}' not in {a_file}")
                    elif match_count > 50:
                        overly_broad.append(f"SPEC-{spec_id}: '{a_pattern}' matches {match_count}x in {a_file}")
                except Exception:
                    pass  # Binary file or encoding issue — skip

    # Filter duplicates to only those shared across >1 spec
    actual_dupes = {k: v for k, v in duplicate_pairs.items() if len(v) > 1}
    dupe_details = [
        f"({f}, '{p}'): {', '.join(f'SPEC-{s}' for s in sids)}" for (f, p), sids in list(actual_dupes.items())[:20]
    ]

    findings["stale_file_references"] = {"count": len(stale_files), "items": stale_files}
    _print_check(
        "Stale file references (file doesn't exist)",
        "finding" if stale_files else "pass",
        len(stale_files),
        stale_files,
    )

    findings["dead_patterns"] = {"count": len(dead_patterns), "items": dead_patterns}
    _print_check(
        "Dead patterns (file exists, pattern not found)",
        "finding" if dead_patterns else "pass",
        len(dead_patterns),
        dead_patterns,
    )

    findings["overly_broad_patterns"] = {"count": len(overly_broad), "items": overly_broad}
    _print_check(
        "Overly broad patterns (>50 matches)", "finding" if overly_broad else "pass", len(overly_broad), overly_broad
    )

    findings["duplicate_assertion_pairs"] = {"count": len(actual_dupes), "items": dupe_details}
    _print_check(
        "Duplicate (file, pattern) across specs", "finding" if actual_dupes else "pass", len(actual_dupes), dupe_details
    )

    findings["retired_with_assertions"] = {
        "count": len(retired_with_assertions),
        "spec_ids": retired_with_assertions,
    }
    _print_check(
        "Retired specs still carrying assertions",
        "finding" if retired_with_assertions else "pass",
        len(retired_with_assertions),
        [f"SPEC-{s}" for s in retired_with_assertions[:10]],
    )

    return findings


# ===================================================================
# TRACK 3: Configuration Drift Detection (live API)
# ===================================================================


def track_3_config_drift(db: KnowledgeDB) -> dict:
    """Compare code defaults vs live API state, staging vs production."""
    _print_header("Track 3: Configuration Drift Detection (live)")

    try:
        import requests
    except ImportError:
        print("  [SKIP] requests library not available — install with: pip install requests")
        return {"skipped": True, "reason": "requests not installed"}

    findings = {}
    staging_url = os.environ.get("STAGING_URL", "")  # SPEC-0058: No hardcoded FQDNs
    prod_url = os.environ.get("PROD_URL", "")  # SPEC-0058: No hardcoded FQDNs

    # 3a. Version parity — compare source PRODUCT_VERSION vs deployed
    source_version = None
    ver_file = PROJECT_ROOT / "src" / "multi_tenant" / "api_versioning.py"
    if ver_file.exists():
        match = re.search(r'PRODUCT_VERSION\s*=\s*"([^"]+)"', ver_file.read_text())
        if match:
            source_version = match.group(1)

    version_checks = []
    for env_name, base_url in [("staging", staging_url), ("production", prod_url)]:
        try:
            r = requests.get(f"{base_url}/health", timeout=10)
            deployed_version = r.headers.get("x-product-version", "unknown")
            match = source_version == deployed_version
            status = "MATCH" if match else "MISMATCH"
            version_checks.append(
                {
                    "env": env_name,
                    "source": source_version,
                    "deployed": deployed_version,
                    "status": status,
                }
            )
            icon = "PASS" if match else "FIND"
            print(f"  [{icon}] {env_name} version: source={source_version}, deployed={deployed_version}")
        except Exception as e:
            version_checks.append({"env": env_name, "error": str(e)})
            print(f"  [SKIP] {env_name} health: {e}")

    findings["version_parity"] = version_checks

    # 3b. Staging vs production version parity
    staging_ver = next((v["deployed"] for v in version_checks if v.get("env") == "staging" and "deployed" in v), None)
    prod_ver = next((v["deployed"] for v in version_checks if v.get("env") == "production" and "deployed" in v), None)
    if staging_ver and prod_ver:
        match = staging_ver == prod_ver
        findings["env_version_parity"] = {
            "staging": staging_ver,
            "production": prod_ver,
            "status": "MATCH" if match else "MISMATCH",
        }
        icon = "PASS" if match else "FIND"
        print(f"  [{icon}] Staging vs production: staging={staging_ver}, production={prod_ver}")

    # 3c. Health endpoint content comparison (unauthenticated fields)
    for env_name, base_url in [("staging", staging_url), ("production", prod_url)]:
        try:
            r = requests.get(f"{base_url}/health", timeout=10)
            if r.status_code == 200:
                body = r.json()
                findings[f"{env_name}_health"] = {
                    "status": r.status_code,
                    "product_version": body.get("product_version"),
                    "api_version": body.get("api_version"),
                }
        except Exception:
            pass

    return findings


# ===================================================================
# TRACK 4: Source File Consistency
# ===================================================================


def track_4_file_consistency(db: KnowledgeDB) -> dict:
    """Verify that files referenced in KB records still exist."""
    _print_header("Track 4: Source File Consistency")
    conn = db._get_conn()
    findings = {}

    # 4a. Test file references — do test_file paths exist on disk?
    test_files = conn.execute("""
        SELECT DISTINCT test_file FROM current_tests
        WHERE test_file IS NOT NULL AND test_file != ''
    """).fetchall()
    missing_test_files = []
    for row in test_files:
        tf = row["test_file"]
        full = PROJECT_ROOT / tf
        if not full.exists():
            missing_test_files.append(tf)
    findings["missing_test_files"] = {"count": len(missing_test_files), "files": missing_test_files}
    _print_check(
        "Test artifacts with missing test_file",
        "finding" if missing_test_files else "pass",
        len(missing_test_files),
        missing_test_files,
    )

    # 4b. Protected Behavior assertion files exist
    pb_specs = conn.execute("""
        SELECT id, assertions FROM current_specifications
        WHERE (id LIKE 'PB-%' OR type = 'protected_behavior')
          AND assertions IS NOT NULL
    """).fetchall()
    pb_missing = []
    for spec in pb_specs:
        try:
            assertions = json.loads(spec["assertions"])
        except (json.JSONDecodeError, TypeError):
            continue
        for a in assertions if isinstance(assertions, list) else []:
            f = a.get("file", "")
            if f and not (PROJECT_ROOT / f).exists():
                pb_missing.append(f"PB {spec['id']}: {f}")
    findings["pb_missing_files"] = {"count": len(pb_missing), "items": pb_missing}
    _print_check(
        "Protected Behavior assertion files missing", "finding" if pb_missing else "pass", len(pb_missing), pb_missing
    )

    # 4c. Admin SPA dist freshness
    dist_freshness = []
    for spa in ["standalone", "shopify", "provider"]:
        dist_dir = PROJECT_ROOT / "admin" / spa / "dist"
        src_dir = PROJECT_ROOT / "admin" / spa / "src"
        if not dist_dir.exists():
            dist_freshness.append(f"{spa}: dist/ missing")
            continue
        if not src_dir.exists():
            continue

        # Find latest mtime in src/ and dist/
        src_latest = max(
            (f.stat().st_mtime for f in src_dir.rglob("*") if f.is_file()),
            default=0,
        )
        dist_latest = max(
            (f.stat().st_mtime for f in dist_dir.rglob("*") if f.is_file()),
            default=0,
        )
        if src_latest > dist_latest and dist_latest > 0:
            delta_hours = (src_latest - dist_latest) / 3600
            dist_freshness.append(f"{spa}: src is {delta_hours:.1f}h newer than dist (stale build)")
    findings["dist_freshness"] = {"count": len(dist_freshness), "items": dist_freshness}
    _print_check(
        "Admin SPA dist freshness", "finding" if dist_freshness else "pass", len(dist_freshness), dist_freshness
    )

    # 4d. test_coverage referencing missing test files
    cov_files = conn.execute("""
        SELECT DISTINCT test_file FROM test_coverage
        WHERE test_file IS NOT NULL AND test_file != ''
    """).fetchall()
    missing_cov_files = []
    for row in cov_files:
        tf = row["test_file"]
        full = PROJECT_ROOT / tf
        if not full.exists():
            missing_cov_files.append(tf)
    findings["missing_coverage_files"] = {
        "count": len(missing_cov_files),
        "files": missing_cov_files,
    }
    _print_check(
        "test_coverage entries with missing test_file",
        "finding" if missing_cov_files else "pass",
        len(missing_cov_files),
        missing_cov_files,
    )

    return findings


# ===================================================================
# TRACK 5: Process Efficiency Metrics
# ===================================================================


def track_5_efficiency(db: KnowledgeDB) -> dict:
    """Aggregate metrics revealing process overhead or waste."""
    _print_header("Track 5: Process Efficiency Metrics")
    conn = db._get_conn()
    findings = {}

    # 5a. Spec version churn — specs with >5 versions
    high_churn = conn.execute("""
        SELECT id, MAX(version) as max_v, COUNT(*) as versions
        FROM specifications
        GROUP BY id
        HAVING COUNT(*) > 5
        ORDER BY COUNT(*) DESC
        LIMIT 20
    """).fetchall()
    churn_items = [f"SPEC-{r['id']}: {r['versions']} versions" for r in high_churn]
    findings["high_churn_specs"] = {"count": len(high_churn), "items": churn_items}
    _print_check(
        "Specs with >5 versions (high churn)", "finding" if high_churn else "pass", len(high_churn), churn_items
    )

    # 5b. KB table sizes (row counts)
    tables = [
        "specifications",
        "test_procedures",
        "operational_procedures",
        "assertion_runs",
        "session_prompts",
        "environment_config",
        "documents",
        "test_coverage",
        "tests",
        "test_plans",
        "test_plan_phases",
        "work_items",
        "backlog_snapshots",
        "testable_elements",
    ]
    table_sizes = {}
    for t in tables:
        try:
            cnt = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            table_sizes[t] = cnt
        except Exception:
            table_sizes[t] = -1
    findings["table_sizes"] = table_sizes
    total_rows = sum(v for v in table_sizes.values() if v > 0)
    print(f"  [INFO] Total KB rows: {total_rows:,}")
    for t, cnt in sorted(table_sizes.items(), key=lambda x: -x[1]):
        if cnt > 100:
            print(f"         {t}: {cnt:,}")

    # 5c. Session script accumulation
    session_scripts = list(SCRIPT_DIR.glob("s1[0-9]*_*.py"))
    record_scripts = list(SCRIPT_DIR.glob("record_*.py"))
    findings["script_accumulation"] = {
        "session_scripts": len(session_scripts),
        "record_scripts": len(record_scripts),
        "total": len(session_scripts) + len(record_scripts),
    }
    _print_check(
        "One-off script accumulation (session + record)",
        "finding" if len(session_scripts) + len(record_scripts) > 80 else "pass",
        len(session_scripts) + len(record_scripts),
        [f"{len(session_scripts)} session scripts, {len(record_scripts)} record scripts"],
    )

    # 5d. WI resolution rate
    resolved = conn.execute("""
        SELECT COUNT(*) FROM current_work_items WHERE resolution_status = 'resolved'
    """).fetchone()[0]
    open_count = conn.execute("""
        SELECT COUNT(*) FROM current_work_items WHERE resolution_status = 'open'
    """).fetchone()[0]
    total_wis = conn.execute("SELECT COUNT(*) FROM current_work_items").fetchone()[0]
    findings["wi_resolution"] = {
        "open": open_count,
        "resolved": resolved,
        "total": total_wis,
        "resolution_rate": round(resolved / total_wis * 100, 1) if total_wis else 0,
    }
    print(
        f"  [INFO] WI resolution rate: {findings['wi_resolution']['resolution_rate']}% "
        f"({resolved}/{total_wis}, {open_count} open)"
    )

    # 5e. Spec status distribution
    summary = db.get_summary()
    findings["spec_distribution"] = summary.get("spec_counts", {})
    print(f"  [INFO] Spec status distribution:")
    for status, cnt in sorted(summary.get("spec_counts", {}).items()):
        print(f"         {status}: {cnt}")

    return findings


# ===================================================================
# Main
# ===================================================================


def main() -> None:
    parser = argparse.ArgumentParser(description="Project Integrity Scan")
    parser.add_argument("--live", action="store_true", help="Include Track 3 (live API calls to staging/production)")
    parser.add_argument(
        "--track", nargs="+", type=int, default=None, help="Run specific tracks only (e.g., --track 1 2)"
    )
    parser.add_argument("--json", action="store_true", help="Save JSON report to integrity-results/")
    args = parser.parse_args()

    tracks_to_run = set(args.track) if args.track else {1, 2, 3, 4, 5}

    # Skip Track 3 unless --live is specified
    if 3 in tracks_to_run and not args.live:
        tracks_to_run.discard(3)

    print("=" * 60)
    print("  Agent Red Project Integrity Scan")
    print(f"  {_now_iso()}")
    print(f"  Tracks: {sorted(tracks_to_run)}")
    print("=" * 60)

    db = KnowledgeDB()
    report = {"timestamp": _now_iso(), "tracks": {}}
    start = time.time()

    if 1 in tracks_to_run:
        report["tracks"]["1_kb_integrity"] = track_1_kb_integrity(db)
    if 2 in tracks_to_run:
        report["tracks"]["2_assertion_validity"] = track_2_assertion_validity(db)
    if 3 in tracks_to_run:
        report["tracks"]["3_config_drift"] = track_3_config_drift(db)
    if 4 in tracks_to_run:
        report["tracks"]["4_file_consistency"] = track_4_file_consistency(db)
    if 5 in tracks_to_run:
        report["tracks"]["5_efficiency"] = track_5_efficiency(db)

    elapsed = time.time() - start
    report["elapsed_seconds"] = round(elapsed, 1)

    # Summary
    total_findings = 0
    for track_data in report["tracks"].values():
        if isinstance(track_data, dict):
            for key, val in track_data.items():
                if isinstance(val, dict) and "count" in val and val["count"] > 0:
                    total_findings += 1

    _print_header("SUMMARY")
    print(f"  Elapsed: {elapsed:.1f}s")
    print(f"  Tracks run: {len(report['tracks'])}")
    print(f"  Finding categories with >0 items: {total_findings}")
    if total_findings == 0:
        print("  Result: CLEAN")
    else:
        print(f"  Result: {total_findings} finding categories need review")

    # Optional JSON output
    if args.json:
        RESULTS_DIR.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        out_path = RESULTS_DIR / f"scan-{ts}.json"
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n  JSON report: {out_path}")

    db.close()


if __name__ == "__main__":
    main()
