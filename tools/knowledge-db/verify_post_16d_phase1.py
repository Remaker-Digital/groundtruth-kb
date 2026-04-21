#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""POR Step 16.D Phase 1 — phantom spec-link cleanup + verification.

Three modes:
- --dry-run: Query live KB; report phantom-link count + distinct IDs. No mutation.
- --apply:   For each phantom-linked test, call update_test(..., spec_id="", ...).
             Also writes a pre-apply snapshot file for I4 verification.
- --verify:  Assert the 4 Phase 1 invariants (I1-I4); exit non-zero on any FAIL.

Phantom = latest-version test whose spec_id is non-empty but does not resolve
to ANY spec in specifications (any version). This script is a one-shot
Phase 1 operation, not a persistent CI gate.

Per bridge/por-step16d-phantom-link-cleanup-004.md GO conditions 1-5.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = REPO_ROOT / "groundtruth.db"
SNAPSHOT_PATH = REPO_ROOT / ".groundtruth" / "por-16d-phase1-snapshot.json"


def _phantom_query() -> str:
    """SQL for latest-version tests with phantom spec_id."""
    return """
    WITH latest AS (
      SELECT t.* FROM tests t
      WHERE t.version = (SELECT MAX(version) FROM tests t2 WHERE t2.id = t.id)
    )
    SELECT id, version, spec_id, test_file, test_class, test_function
    FROM latest
    WHERE spec_id IS NOT NULL AND spec_id != ''
      AND NOT EXISTS (
          SELECT 1 FROM specifications s WHERE s.id = latest.spec_id
      )
    ORDER BY id
    """


def _baseline_counts(conn: sqlite3.Connection) -> dict[str, int]:
    """Return the four baseline counts shown in the proposal."""
    sql = """
    WITH latest AS (
      SELECT t.* FROM tests t
      WHERE t.version = (SELECT MAX(version) FROM tests t2 WHERE t2.id = t.id)
    )
    SELECT
      COUNT(*) AS total,
      SUM(CASE WHEN spec_id = '' THEN 1 ELSE 0 END) AS empty_spec_id,
      SUM(CASE WHEN spec_id IS NOT NULL AND spec_id != ''
               AND NOT EXISTS (SELECT 1 FROM specifications s WHERE s.id = latest.spec_id)
               THEN 1 ELSE 0 END) AS phantom_spec_id,
      SUM(CASE WHEN spec_id IS NOT NULL AND spec_id != ''
               AND EXISTS (SELECT 1 FROM specifications s WHERE s.id = latest.spec_id)
               THEN 1 ELSE 0 END) AS valid_spec_link
    FROM latest
    """
    row = conn.execute(sql).fetchone()
    return {
        "total": row[0],
        "empty_spec_id": row[1],
        "phantom_spec_id": row[2],
        "valid_spec_link": row[3],
    }


def cmd_dry_run() -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        counts = _baseline_counts(conn)
        print(f"Baseline: {counts}")
        phantoms = conn.execute(_phantom_query()).fetchall()
        distinct_spec_ids = sorted({row[2] for row in phantoms})
        print(f"Phantom links found: {len(phantoms)} ({len(distinct_spec_ids)} distinct spec_id values)")
        print("Distinct phantom spec_ids:")
        for sid in distinct_spec_ids:
            cnt = sum(1 for row in phantoms if row[2] == sid)
            print(f"  {sid}: {cnt} tests")
        print("Sample affected test IDs (first 5):")
        for row in phantoms[:5]:
            print(f"  {row[0]}  (spec_id={row[2]!r}, file={row[3]})")
        print("\nDry-run complete. No mutation.")
        return 0
    finally:
        conn.close()


def cmd_apply() -> int:
    # Import KnowledgeDB from the project tooling.
    sys.path.insert(0, str(REPO_ROOT / "tools" / "knowledge-db"))
    from db import KnowledgeDB  # noqa: E402  (late import is deliberate)

    conn = sqlite3.connect(DB_PATH)
    try:
        baseline = _baseline_counts(conn)
        print(f"Pre-apply baseline: {baseline}")
        phantoms = conn.execute(_phantom_query()).fetchall()
        print(f"Will mutate {len(phantoms)} tests (set spec_id to empty string).")
    finally:
        conn.close()

    if not phantoms:
        print("No phantoms found. Nothing to apply.")
        return 0

    # Write pre-apply snapshot (I4 evidence + audit trail).
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "phase": "POR-16D-Phase-1",
        "baseline_before_apply": baseline,
        "affected_tests": [
            {
                "id": row[0],
                "version_before_apply": row[1],
                "spec_id_before_apply": row[2],
                "test_file": row[3],
                "test_class": row[4],
                "test_function": row[5],
            }
            for row in phantoms
        ],
    }
    SNAPSHOT_PATH.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Snapshot written: {SNAPSHOT_PATH.relative_to(REPO_ROOT)}")

    # Apply mutations.
    db = KnowledgeDB(str(DB_PATH))
    mutated = 0
    for row in phantoms:
        test_id = row[0]
        old_spec_id = row[2]
        db.update_test(
            test_id,
            changed_by="por_step16d_phase1",
            change_reason=(
                f"Phantom spec_id cleared per POR Step 16.D Phase 1 — "
                f"old spec_id={old_spec_id!r} did not resolve to any KB specification"
            ),
            spec_id="",
        )
        mutated += 1
        if mutated % 200 == 0:
            print(f"  ...{mutated}/{len(phantoms)} applied")

    print(f"\nApplied {mutated} updates.")

    # Report post-apply count.
    conn = sqlite3.connect(DB_PATH)
    try:
        final = _baseline_counts(conn)
        print(f"Post-apply baseline: {final}")
        print(
            f"Final empty-spec count: {final['empty_spec_id']} "
            f"(expected {baseline['empty_spec_id'] + mutated})"
        )
    finally:
        conn.close()
    return 0


def cmd_verify() -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        counts = _baseline_counts(conn)

        results: list[tuple[str, bool, str]] = []

        # I1: no phantom links remain.
        i1_pass = counts["phantom_spec_id"] == 0
        results.append(
            (
                "I1",
                i1_pass,
                f"phantom links = {counts['phantom_spec_id']} (expected 0)",
            )
        )

        # I2: total latest-version test count = 11,142.
        i2_pass = counts["total"] == 11142
        results.append(
            ("I2", i2_pass, f"total latest tests = {counts['total']} (expected 11142)")
        )

        # I3: empty-spec count = 2,322.
        i3_pass = counts["empty_spec_id"] == 2322
        results.append(
            (
                "I3",
                i3_pass,
                f"empty spec_id = {counts['empty_spec_id']} (expected 2322)",
            )
        )

        # I4: 2,068 test IDs have version > pre-apply snapshot.
        if not SNAPSHOT_PATH.exists():
            results.append(
                (
                    "I4",
                    False,
                    "SKIP-NO-SNAPSHOT: snapshot file missing; treated as FAIL per "
                    "bridge/por-step16d-phantom-link-cleanup-004.md condition 3",
                )
            )
        else:
            snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
            mutated_count = 0
            affected_tests = snapshot["affected_tests"]
            for row in affected_tests:
                test_id = row["id"]
                pre_version = row["version_before_apply"]
                cur_version_row = conn.execute(
                    "SELECT MAX(version) FROM tests WHERE id = ?", (test_id,)
                ).fetchone()
                cur_version = cur_version_row[0] if cur_version_row else None
                if cur_version is not None and cur_version > pre_version:
                    mutated_count += 1
            i4_pass = mutated_count == 2068
            results.append(
                (
                    "I4",
                    i4_pass,
                    f"version-increment count = {mutated_count} of "
                    f"{len(affected_tests)} snapshot IDs (expected 2068)",
                )
            )

        all_pass = all(r[1] for r in results)
        print("Phase 1 verification:")
        for name, passed, detail in results:
            marker = "PASS" if passed else "FAIL"
            print(f"  {marker}: {name} - {detail}")
        print(f"\nOverall: {'PASS' if all_pass else 'FAIL'}")
        return 0 if all_pass else 1
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="POR Step 16.D Phase 1 — phantom spec-link cleanup"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Report phantom links; no mutation")
    group.add_argument("--apply", action="store_true", help="Apply cleanup + write snapshot")
    group.add_argument("--verify", action="store_true", help="Assert I1-I4 invariants")
    args = parser.parse_args()

    if args.dry_run:
        return cmd_dry_run()
    if args.apply:
        return cmd_apply()
    if args.verify:
        return cmd_verify()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
