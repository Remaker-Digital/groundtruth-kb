#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""POR Step 16.D Phase 2 - orphan-test sibling-match auto-link + classification report.

Three modes:
- --dry-run: Report Class A sibling-match candidates + preview A/B/C/D classification
             (precedence A -> D -> B -> C). No mutation.
- --apply:   Auto-link Class A orphans via KnowledgeDB.update_test(spec_id=<sibling_spec_id>).
             Writes snapshot + classification report files.
- --verify:  Assert 6 Phase 2 invariants (I1-I6) per bridge GO conditions.

Per bridge/por-step16d-orphan-triage-phase2-002.md GO conditions 1-7.

Conflict policy (GO condition 2): fail-closed if any orphan has multiple
candidate siblings with differing spec_ids. No silent tie-break.
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
SNAPSHOT_PATH = REPO_ROOT / ".groundtruth" / "por-16d-phase2-snapshot.json"
CLASSIFICATION_PATH = REPO_ROOT / ".groundtruth" / "por-16d-phase2-classification.json"

EXPECTED_TOTAL_ORPHANS = 2322  # post-Phase-1 baseline
EXPECTED_TOTAL_TESTS = 11142
EXPECTED_CLASS_A = 133  # pre-apply; post-apply = 0
EXPECTED_POST_APPLY_ORPHANS = EXPECTED_TOTAL_ORPHANS - EXPECTED_CLASS_A  # 2189


def _latest_orphans(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    sql = """
    WITH latest AS (
      SELECT t.* FROM tests t
      WHERE t.version = (SELECT MAX(version) FROM tests t2 WHERE t2.id = t.id)
    )
    SELECT id, version, test_file, test_class, test_function, title,
           SUBSTR(COALESCE(description, ''), 1, 120) AS desc_head
    FROM latest
    WHERE spec_id = ''
    ORDER BY id
    """
    rows = conn.execute(sql).fetchall()
    return [
        {
            "id": r[0],
            "version": r[1],
            "test_file": r[2],
            "test_class": r[3] or "",
            "test_function": r[4],
            "title": r[5] or "",
            "desc_head": r[6] or "",
        }
        for r in rows
    ]


def _sibling_matches(conn: sqlite3.Connection, orphans: list[dict[str, Any]]) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]]
]:
    """Return (matches, conflicts).

    A sibling-match for orphan O: another latest-version test S where
    - S.test_file == O.test_file (non-empty)
    - COALESCE(S.test_class, '') == COALESCE(O.test_class, '')
    - S.test_function == O.test_function
    - S.spec_id non-empty AND resolves to an existing spec (any version)
    - S.id != O.id

    matches = list of {orphan_id, sibling_id, spec_id, test_file, test_class, test_function}
    conflicts = list of {orphan_id, candidate_spec_ids: [...]} (len(spec_ids) > 1)

    Per GO condition 2: we DO NOT silently pick earliest-changed_at; multiple
    differing spec_ids triggers conflict for fail-closed handling.
    """
    sql = """
    WITH latest AS (
      SELECT t.* FROM tests t
      WHERE t.version = (SELECT MAX(version) FROM tests t2 WHERE t2.id = t.id)
    )
    SELECT id, test_file, test_class, test_function, spec_id
    FROM latest
    WHERE test_file IS NOT NULL AND test_file != ''
      AND spec_id != ''
      AND EXISTS (SELECT 1 FROM specifications s WHERE s.id = latest.spec_id)
    """
    linked_tests = conn.execute(sql).fetchall()

    # Index: (test_file, test_class_norm, test_function) -> set[spec_id]
    triple_to_specs: dict[tuple[str, str, str], set[str]] = {}
    triple_to_sibling: dict[tuple[str, str, str], str] = {}
    for row in linked_tests:
        tid, tfile, tclass, tfunc, sid = row
        if not tfile or not tfunc:
            continue
        key = (tfile, tclass or "", tfunc)
        triple_to_specs.setdefault(key, set()).add(sid)
        triple_to_sibling.setdefault(key, tid)

    matches: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    for orphan in orphans:
        if not orphan["test_file"] or not orphan["test_function"]:
            continue
        key = (orphan["test_file"], orphan["test_class"], orphan["test_function"])
        candidate_specs = triple_to_specs.get(key)
        if not candidate_specs:
            continue
        if len(candidate_specs) == 1:
            spec_id = next(iter(candidate_specs))
            sibling_id = triple_to_sibling[key]
            matches.append(
                {
                    "orphan_id": orphan["id"],
                    "orphan_version_before_apply": orphan["version"],
                    "sibling_id": sibling_id,
                    "target_spec_id": spec_id,
                    "test_file": orphan["test_file"],
                    "test_class": orphan["test_class"],
                    "test_function": orphan["test_function"],
                }
            )
        else:
            conflicts.append(
                {
                    "orphan_id": orphan["id"],
                    "test_file": orphan["test_file"],
                    "test_class": orphan["test_class"],
                    "test_function": orphan["test_function"],
                    "candidate_spec_ids": sorted(candidate_specs),
                }
            )
    return matches, conflicts


def _classify_disjoint(
    conn: sqlite3.Connection,
    orphans: list[dict[str, Any]],
    class_a_ids: set[str],
) -> dict[str, list[dict[str, Any]]]:
    """Build disjoint A/B/C/D classes per GO condition precedence A -> D -> B -> C.

    - A: already-selected sibling-match IDs (passed in).
    - D: test_file is NULL or empty (stale records).
    - B: test_file exists AND at least one OTHER test in the same file links to an existing spec.
    - C: the remainder (fully-orphaned files, no cross-file spec link).
    """
    # Pre-compute: for each test_file, does any non-orphan test link to a real spec?
    sql = """
    WITH latest AS (
      SELECT t.* FROM tests t
      WHERE t.version = (SELECT MAX(version) FROM tests t2 WHERE t2.id = t.id)
    )
    SELECT DISTINCT test_file FROM latest
    WHERE test_file IS NOT NULL AND test_file != ''
      AND spec_id != ''
      AND EXISTS (SELECT 1 FROM specifications s WHERE s.id = latest.spec_id)
    """
    files_with_linked_tests = {row[0] for row in conn.execute(sql).fetchall()}

    class_b: list[dict[str, Any]] = []
    class_c_by_file: dict[str, list[str]] = {}
    class_d: list[dict[str, Any]] = []

    for orphan in orphans:
        if orphan["id"] in class_a_ids:
            continue
        tfile = orphan["test_file"]
        if not tfile:
            class_d.append(
                {"test_id": orphan["id"], "test_file": tfile, "reason": "test_file NULL or empty"}
            )
            continue
        if tfile in files_with_linked_tests:
            class_b.append(
                {
                    "test_id": orphan["id"],
                    "test_file": tfile,
                    "test_class": orphan["test_class"],
                    "test_function": orphan["test_function"],
                }
            )
        else:
            class_c_by_file.setdefault(tfile, []).append(orphan["id"])

    class_c = [
        {"test_file": tfile, "orphan_count": len(ids), "sample_test_ids": ids[:5]}
        for tfile, ids in sorted(class_c_by_file.items(), key=lambda kv: -len(kv[1]))
    ]

    return {"B_file_bucket": class_b, "C_fully_orphaned_file": class_c, "D_null_or_missing": class_d}


def _print_summary(matches: list[dict[str, Any]], conflicts: list[dict[str, Any]],
                   classes: dict[str, list[dict[str, Any]]]) -> None:
    class_c_orphan_count = sum(entry["orphan_count"] for entry in classes["C_fully_orphaned_file"])
    print(f"Class A sibling-match candidates: {len(matches)}")
    print(f"Sibling-match conflicts (fail-closed trigger): {len(conflicts)}")
    print(f"Class B file-bucket: {len(classes['B_file_bucket'])}")
    print(f"Class C fully-orphaned files: {len(classes['C_fully_orphaned_file'])} files covering {class_c_orphan_count} tests")
    print(f"Class D NULL or missing: {len(classes['D_null_or_missing'])}")
    total = len(matches) + len(classes["B_file_bucket"]) + class_c_orphan_count + len(classes["D_null_or_missing"])
    print(f"Disjoint sum (A+B+C+D, including conflicts-as-A-eligible): {total}")
    print(f"Expected total orphans: {EXPECTED_TOTAL_ORPHANS}")


def cmd_dry_run() -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        orphans = _latest_orphans(conn)
        print(f"Total orphans (empty spec_id): {len(orphans)}")
        matches, conflicts = _sibling_matches(conn, orphans)
        if conflicts:
            print(f"\nFAIL-CLOSED: {len(conflicts)} orphans have multiple candidate sibling spec_ids:")
            for c in conflicts[:5]:
                print(f"  {c['orphan_id']} -> {c['candidate_spec_ids']}")
            print("Per GO condition 2, --apply will refuse to mutate until policy is revised.")
        class_a_ids = {m["orphan_id"] for m in matches}
        classes = _classify_disjoint(conn, orphans, class_a_ids)
        _print_summary(matches, conflicts, classes)
        print("\nDry-run complete. No mutation.")
        return 1 if conflicts else 0
    finally:
        conn.close()


def cmd_apply() -> int:
    sys.path.insert(0, str(REPO_ROOT / "tools" / "knowledge-db"))
    from db import KnowledgeDB  # noqa: E402

    conn = sqlite3.connect(DB_PATH)
    try:
        orphans = _latest_orphans(conn)
        matches, conflicts = _sibling_matches(conn, orphans)
        if conflicts:
            print(f"ERROR: {len(conflicts)} conflict rows found. Fail-closed per GO condition 2.")
            print("First 5 conflicts:")
            for c in conflicts[:5]:
                print(f"  {c['orphan_id']} -> {c['candidate_spec_ids']}")
            return 2
        class_a_ids = {m["orphan_id"] for m in matches}
        classes = _classify_disjoint(conn, orphans, class_a_ids)
    finally:
        conn.close()

    # Write pre-apply snapshot (GO condition 3).
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "phase": "POR-16D-Phase-2",
        "as_of_pre_apply": True,
        "class_a_matches": matches,
    }
    SNAPSHOT_PATH.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Snapshot written: {SNAPSHOT_PATH.relative_to(REPO_ROOT)}")

    # Write classification report (GO condition 4).
    classification = {
        "phase": "POR-16D-Phase-2",
        "as_of_pre_apply": True,
        "counts": {
            "A_sibling_match": len(matches),
            "B_file_bucket": len(classes["B_file_bucket"]),
            "C_fully_orphaned_file_tests": sum(
                e["orphan_count"] for e in classes["C_fully_orphaned_file"]
            ),
            "C_fully_orphaned_files": len(classes["C_fully_orphaned_file"]),
            "D_null_or_missing": len(classes["D_null_or_missing"]),
        },
        "A_sibling_match": matches,
        "B_file_bucket": classes["B_file_bucket"],
        "C_fully_orphaned_file": classes["C_fully_orphaned_file"],
        "D_null_or_missing": classes["D_null_or_missing"],
    }
    CLASSIFICATION_PATH.write_text(
        json.dumps(classification, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Classification written: {CLASSIFICATION_PATH.relative_to(REPO_ROOT)}")

    # Apply Class A links.
    db = KnowledgeDB(str(DB_PATH))
    applied = 0
    for m in matches:
        db.update_test(
            m["orphan_id"],
            changed_by="por_step16d_phase2",
            change_reason=(
                f"Auto-linked via sibling-match - same (test_file, test_class, test_function) "
                f"triple as {m['sibling_id']} which links to {m['target_spec_id']}"
            ),
            spec_id=m["target_spec_id"],
        )
        applied += 1
        if applied % 50 == 0:
            print(f"  ...{applied}/{len(matches)} applied")

    print(f"\nApplied {applied} Class A auto-links.")

    conn = sqlite3.connect(DB_PATH)
    try:
        post = conn.execute("""
          WITH latest AS (
            SELECT t.* FROM tests t
            WHERE t.version = (SELECT MAX(version) FROM tests t2 WHERE t2.id = t.id)
          )
          SELECT COUNT(*), SUM(CASE WHEN spec_id = '' THEN 1 ELSE 0 END) FROM latest
        """).fetchone()
        print(f"Post-apply: total={post[0]}, empty-spec orphans={post[1]}")
    finally:
        conn.close()
    return 0


def cmd_verify() -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        results: list[tuple[str, bool, str]] = []

        # Baseline counts
        total = conn.execute(
            "SELECT COUNT(*) FROM (SELECT id, MAX(version) FROM tests GROUP BY id)"
        ).fetchone()[0]
        empty_count = conn.execute("""
          WITH latest AS (
            SELECT t.* FROM tests t
            WHERE t.version = (SELECT MAX(version) FROM tests t2 WHERE t2.id = t.id)
          )
          SELECT COUNT(*) FROM latest WHERE spec_id = ''
        """).fetchone()[0]

        # Class A remaining count
        orphans = _latest_orphans(conn)
        matches, conflicts = _sibling_matches(conn, orphans)
        class_a_remaining = len(matches)

        # I1: Class A remaining = 0.
        results.append(("I1", class_a_remaining == 0,
                        f"Class A remaining = {class_a_remaining} (expected 0)"))

        # I2: total latest tests = 11142.
        results.append(("I2", total == EXPECTED_TOTAL_TESTS,
                        f"total latest tests = {total} (expected {EXPECTED_TOTAL_TESTS})"))

        # I3: empty-spec orphans = 2189.
        results.append(("I3", empty_count == EXPECTED_POST_APPLY_ORPHANS,
                        f"empty spec_id = {empty_count} (expected {EXPECTED_POST_APPLY_ORPHANS})"))

        # I4: classification report exists with 4 class keys (A/B/C/D).
        if not CLASSIFICATION_PATH.exists():
            results.append(("I4", False, "classification JSON missing"))
        else:
            report = json.loads(CLASSIFICATION_PATH.read_text(encoding="utf-8"))
            expected_keys = {"A_sibling_match", "B_file_bucket", "C_fully_orphaned_file",
                             "D_null_or_missing"}
            has_keys = expected_keys.issubset(report.keys())
            results.append(("I4", has_keys, f"classification keys present: {has_keys}"))

        # I5: A+B+C+D counts sum to 2322 (pre-apply).
        if CLASSIFICATION_PATH.exists():
            report = json.loads(CLASSIFICATION_PATH.read_text(encoding="utf-8"))
            counts = report.get("counts", {})
            sum_all = (counts.get("A_sibling_match", 0)
                       + counts.get("B_file_bucket", 0)
                       + counts.get("C_fully_orphaned_file_tests", 0)
                       + counts.get("D_null_or_missing", 0))
            results.append(("I5", sum_all == EXPECTED_TOTAL_ORPHANS,
                            f"class sum = {sum_all} (expected {EXPECTED_TOTAL_ORPHANS})"))
        else:
            results.append(("I5", False, "no classification file to sum"))

        # I6: all 133 snapshot IDs have (a) version increment, (b) changed_by=por_step16d_phase2,
        #     (c) spec_id == target_spec_id.
        if not SNAPSHOT_PATH.exists():
            results.append(("I6", False, "snapshot missing (FAIL per GO condition 5)"))
        else:
            snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
            sids = snapshot["class_a_matches"]
            ok = 0
            problems: list[str] = []
            for m in sids:
                orphan_id = m["orphan_id"]
                pre_version = m["orphan_version_before_apply"]
                target_spec = m["target_spec_id"]
                row = conn.execute(
                    "SELECT MAX(version) FROM tests WHERE id = ?", (orphan_id,)
                ).fetchone()
                cur_version = row[0] if row else None
                if cur_version is None or cur_version <= pre_version:
                    problems.append(f"{orphan_id} version did not increment ({pre_version} -> {cur_version})")
                    continue
                row2 = conn.execute(
                    "SELECT spec_id, changed_by FROM tests WHERE id = ? AND version = ?",
                    (orphan_id, cur_version),
                ).fetchone()
                if row2 is None:
                    problems.append(f"{orphan_id} no row at latest version {cur_version}")
                    continue
                new_spec, new_changer = row2[0], row2[1]
                if new_spec != target_spec:
                    problems.append(f"{orphan_id} spec_id={new_spec!r}, expected {target_spec!r}")
                    continue
                if new_changer != "por_step16d_phase2":
                    problems.append(f"{orphan_id} changed_by={new_changer!r}")
                    continue
                ok += 1
            i6_pass = ok == len(sids) and not problems
            detail = f"verified IDs = {ok}/{len(sids)}"
            if problems:
                detail += f"; sample issues: {problems[:3]}"
            results.append(("I6", i6_pass, detail))

        all_pass = all(r[1] for r in results)
        print("Phase 2 verification:")
        for name, passed, detail in results:
            marker = "PASS" if passed else "FAIL"
            print(f"  {marker}: {name} - {detail}")
        print(f"\nOverall: {'PASS' if all_pass else 'FAIL'}")
        return 0 if all_pass else 1
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="POR Step 16.D Phase 2 - orphan-test triage"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Report + classification preview; no mutation")
    group.add_argument("--apply", action="store_true", help="Auto-link Class A + write snapshot/report")
    group.add_argument("--verify", action="store_true", help="Assert I1-I6 invariants")
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
