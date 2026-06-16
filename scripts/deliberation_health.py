#!/usr/bin/env python3
"""
Deliberation Archive health metrics.

SPEC-2098 Phase C4: Reports 5 health metrics with PASS/WARN/FAIL thresholds.

Metrics:
  1. Population coverage  — current_deliberations / candidate source files
  2. Linkage coverage     — deliberations with SPEC/WI links / total
  3. Conflict quarantine  — conflicts without final outcome / total conflicts
  4. Redaction survivors  — always 0 (post-redaction AR keys)
  5. Duplicate suppression — idempotent rerun creates 0 new rows

Usage:
    python scripts/deliberation_health.py
    python scripts/deliberation_health.py --json

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
KB_PATH = REPO_ROOT / "groundtruth.db"
INSIGHT_DIR = REPO_ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX"
BRIDGE_DIR = REPO_ROOT / "bridge"

_AR_KEY_RE = re.compile(r"(ar_live|ar_user|ar_spa_plat|pk_live|arsk)_[A-Za-z0-9_-]{10,}")

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

# Population coverage: PASS >= 80%, WARN >= 50%
POP_PASS = 0.80
POP_WARN = 0.50

# Linkage coverage: PASS >= 40%, WARN >= 20%
LINK_PASS = 0.40
LINK_WARN = 0.20

# Conflict quarantine: PASS = 0, WARN <= 5%
CONFLICT_WARN = 0.05


def _status(value: float, pass_thresh: float, warn_thresh: float) -> str:
    if value >= pass_thresh:
        return "PASS"
    if value >= warn_thresh:
        return "WARN"
    return "FAIL"


def _zero_status(count: int) -> str:
    return "PASS" if count == 0 else "FAIL"


# ---------------------------------------------------------------------------
# Candidate count (sources that should be in archive)
# ---------------------------------------------------------------------------


def count_candidate_sources() -> dict[str, int]:
    """Count files eligible for deliberation archival."""
    lo_count = 0
    if INSIGHT_DIR.exists():
        lo_count = len([f for f in INSIGHT_DIR.glob("INSIGHTS-*.md") if f.stat().st_size >= 100])

    gt_src = REPO_ROOT / "groundtruth-kb" / "src"
    if str(gt_src) not in sys.path:
        sys.path.insert(0, str(gt_src))
    from groundtruth_kb.bridge.versioned_files import scan_expected_documents, status_from_bridge_file

    bridge_count = 0
    seen: set[str] = set()
    for document in scan_expected_documents(REPO_ROOT).values():
        for rel_path in document.files:
            if rel_path in seen:
                continue
            fpath = REPO_ROOT / rel_path
            status = status_from_bridge_file(fpath)
            if status in {"VERIFIED", "GO", "NO-GO"} and fpath.exists() and fpath.stat().st_size >= 100:
                seen.add(rel_path)
                bridge_count += 1

    return {"lo_reports": lo_count, "bridge_threads": bridge_count, "total": lo_count + bridge_count}


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


def check_health(kb_path: str | None = None) -> dict:
    """Run all 5 health metrics."""
    path = kb_path or str(KB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row

    # Current deliberation count
    total_delibs = conn.execute("SELECT COUNT(*) FROM current_deliberations").fetchone()[0]

    # Source type distribution
    source_types = {}
    for row in conn.execute(
        "SELECT source_type, COUNT(*) as cnt FROM current_deliberations GROUP BY source_type"
    ).fetchall():
        source_types[row["source_type"]] = row["cnt"]

    # Candidate sources
    candidates = count_candidate_sources()

    # --- Metric 1: Population coverage ---
    pop_coverage = total_delibs / candidates["total"] if candidates["total"] > 0 else 0.0
    pop_status = _status(pop_coverage, POP_PASS, POP_WARN)

    # --- Metric 2: Linkage coverage ---
    linked_specs = conn.execute("SELECT COUNT(DISTINCT deliberation_id) FROM deliberation_specs").fetchone()[0]
    linked_wis = conn.execute("SELECT COUNT(DISTINCT deliberation_id) FROM deliberation_work_items").fetchone()[0]
    linked_delibs = conn.execute(
        """SELECT COUNT(*) FROM current_deliberations
           WHERE spec_id IS NOT NULL OR work_item_id IS NOT NULL
           OR id IN (SELECT deliberation_id FROM deliberation_specs)
           OR id IN (SELECT deliberation_id FROM deliberation_work_items)"""
    ).fetchone()[0]
    link_coverage = linked_delibs / total_delibs if total_delibs > 0 else 0.0
    link_status = _status(link_coverage, LINK_PASS, LINK_WARN)

    # --- Metric 3: Conflict quarantine ---
    # Conflicts = deliberations with 'informational' outcome that might have been misclassified
    # (those sourced from reports with conflicting verdict signals)
    conflict_count = conn.execute(
        "SELECT COUNT(*) FROM current_deliberations WHERE outcome = 'informational'"
    ).fetchone()[0]
    quarantine_rate = conflict_count / total_delibs if total_delibs > 0 else 0.0
    # Lower is better for conflicts — invert threshold logic
    if quarantine_rate == 0 or quarantine_rate <= CONFLICT_WARN:
        quarantine_status = "PASS"
    else:
        quarantine_status = "WARN"

    # --- Metric 4: Redaction survivors ---
    survivor_count = 0
    for row in conn.execute("SELECT content FROM current_deliberations").fetchall():
        survivor_count += len(_AR_KEY_RE.findall(row["content"]))
    survivor_status = _zero_status(survivor_count)

    # --- Metric 5: Duplicate suppression ---
    # Check for duplicate (source_ref, content_hash) pairs
    dup_count = conn.execute(
        """SELECT COUNT(*) FROM (
           SELECT source_ref, content_hash, COUNT(*) as cnt
           FROM current_deliberations
           WHERE source_ref IS NOT NULL
           GROUP BY source_ref, content_hash
           HAVING cnt > 1)"""
    ).fetchone()[0]
    dup_status = _zero_status(dup_count)

    conn.close()

    metrics = {
        "population": {
            "total_deliberations": total_delibs,
            "candidate_sources": candidates["total"],
            "lo_reports": candidates["lo_reports"],
            "bridge_threads": candidates["bridge_threads"],
            "coverage": round(pop_coverage, 4),
            "status": pop_status,
        },
        "linkage": {
            "linked_deliberations": linked_delibs,
            "total_deliberations": total_delibs,
            "spec_links": linked_specs,
            "wi_links": linked_wis,
            "coverage": round(link_coverage, 4),
            "status": link_status,
        },
        "conflict_quarantine": {
            "informational_outcome": conflict_count,
            "total_deliberations": total_delibs,
            "quarantine_rate": round(quarantine_rate, 4),
            "status": quarantine_status,
        },
        "redaction_survivors": {
            "survivor_count": survivor_count,
            "status": survivor_status,
        },
        "duplicate_suppression": {
            "duplicate_groups": dup_count,
            "status": dup_status,
        },
        "source_types": source_types,
    }

    return metrics


def print_report(metrics: dict) -> None:
    """Print human-readable health report."""
    print("=" * 60)
    print("Deliberation Archive Health Report")
    print("=" * 60)

    pop = metrics["population"]
    print(f"\n1. Population Coverage: [{pop['status']}]")
    print(
        f"   {pop['total_deliberations']} deliberations / {pop['candidate_sources']} candidates = {pop['coverage']:.1%}"
    )
    print(f"   (LO reports: {pop['lo_reports']}, bridge threads: {pop['bridge_threads']})")

    link = metrics["linkage"]
    print(f"\n2. Linkage Coverage: [{link['status']}]")
    print(f"   {link['linked_deliberations']} linked / {link['total_deliberations']} total = {link['coverage']:.1%}")
    print(f"   (spec links: {link['spec_links']}, WI links: {link['wi_links']})")

    conf = metrics["conflict_quarantine"]
    print(f"\n3. Conflict Quarantine: [{conf['status']}]")
    print(
        f"   {conf['informational_outcome']} informational / {conf['total_deliberations']} total = {conf['quarantine_rate']:.1%}"
    )

    red = metrics["redaction_survivors"]
    print(f"\n4. Redaction Survivors: [{red['status']}]")
    print(f"   {red['survivor_count']} AR key survivors in archived content")

    dup = metrics["duplicate_suppression"]
    print(f"\n5. Duplicate Suppression: [{dup['status']}]")
    print(f"   {dup['duplicate_groups']} duplicate (source_ref, content_hash) groups")

    st = metrics["source_types"]
    if st:
        print("\nSource type distribution:")
        for k, v in sorted(st.items()):
            print(f"   {k}: {v}")

    # Overall
    statuses = [pop["status"], link["status"], conf["status"], red["status"], dup["status"]]
    if "FAIL" in statuses:
        overall = "FAIL"
    elif "WARN" in statuses:
        overall = "WARN"
    else:
        overall = "PASS"
    print(f"\nOverall: [{overall}]")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Deliberation archive health check (SPEC-2098 C4)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--kb-path", type=str, default=None, help="Path to groundtruth.db")
    args = parser.parse_args()

    metrics = check_health(args.kb_path)

    if args.json:
        print(json.dumps(metrics, indent=2))
    else:
        print_report(metrics)


if __name__ == "__main__":
    main()
