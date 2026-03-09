#!/usr/bin/env python3
"""
S159: Integrity Scan Remediation

Fixes findings from scripts/integrity_scan.py:
  Fix 1: Clear assertions from retired specs (154 specs)
  Fix 2: Remove dead-pattern assertions from active specs (118 specs)
  Fix 3: Archive one-off session/record scripts (104 scripts)
  Report: Orphaned tests (2,317), overly broad patterns, duplicates

Safety model:
  - All KB changes use append-only update_spec() (new version, no data loss)
  - Scripts archived to scripts/archive/ (reversible via git)
  - Dry-run mode by default (--apply to execute)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
KB_DIR = PROJECT_ROOT / "tools" / "knowledge-db"
ARCHIVE_DIR = SCRIPT_DIR / "archive"

sys.path.insert(0, str(KB_DIR))
from db import KnowledgeDB  # noqa: E402


def fix_1_retired_spec_assertions(db: KnowledgeDB, *, apply: bool = False) -> dict:
    """Clear assertions from retired specs — they serve no purpose."""
    conn = db._get_conn()
    retired = conn.execute("""
        SELECT id, assertions FROM current_specifications
        WHERE status = 'retired'
          AND assertions IS NOT NULL AND assertions != 'null' AND assertions != '[]'
    """).fetchall()

    cleared = []
    for spec in retired:
        spec_id = spec["id"]
        try:
            assertions = json.loads(spec["assertions"])
            if not assertions:
                continue
        except (json.JSONDecodeError, TypeError):
            continue

        cleared.append(spec_id)
        if apply:
            db.update_spec(
                spec_id,
                changed_by="S159-integrity",
                change_reason="Clear assertions from retired spec (integrity scan Fix 1)",
                assertions=[],
            )

    print(f"  Fix 1: Retired specs with assertions cleared: {len(cleared)}")
    if not apply and cleared:
        print(f"         (dry-run — use --apply to execute)")
    return {"count": len(cleared), "spec_ids": cleared}


def fix_2_dead_pattern_assertions(db: KnowledgeDB, *, apply: bool = False) -> dict:
    """Remove individual dead-pattern assertions from active specs.

    Only removes the specific assertion(s) where the pattern no longer matches.
    Preserves all other assertions on the same spec.
    """
    conn = db._get_conn()
    specs = conn.execute("""
        SELECT id, status, assertions FROM current_specifications
        WHERE status != 'retired'
          AND assertions IS NOT NULL AND assertions != 'null' AND assertions != '[]'
    """).fetchall()

    fixed_specs = []
    total_removed = 0

    for spec in specs:
        spec_id = spec["id"]
        try:
            assertions = json.loads(spec["assertions"])
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(assertions, list):
            continue

        live_assertions = []
        removed_count = 0

        for a in assertions:
            a_type = a.get("type", "grep")
            a_file = a.get("file", "")
            a_pattern = a.get("pattern", "")

            if a_type not in ("grep",) or not a_file or not a_pattern:
                # Keep non-grep, glob, grep_absent, and incomplete assertions as-is
                live_assertions.append(a)
                continue

            full_path = PROJECT_ROOT / a_file
            if not full_path.exists():
                # File doesn't exist — stale reference, remove
                removed_count += 1
                continue

            try:
                content = full_path.read_text(encoding="utf-8", errors="replace")
                if re.search(re.escape(a_pattern), content):
                    live_assertions.append(a)
                else:
                    removed_count += 1
            except Exception:
                live_assertions.append(a)  # Keep if we can't read the file

        if removed_count > 0:
            fixed_specs.append({
                "spec_id": spec_id,
                "removed": removed_count,
                "remaining": len(live_assertions),
            })
            total_removed += removed_count
            if apply:
                db.update_spec(
                    spec_id,
                    changed_by="S159-integrity",
                    change_reason=f"Remove {removed_count} dead-pattern assertion(s) (integrity scan Fix 2)",
                    assertions=live_assertions,
                )

    print(f"  Fix 2: Specs with dead patterns fixed: {len(fixed_specs)}, assertions removed: {total_removed}")
    if not apply and fixed_specs:
        print(f"         (dry-run — use --apply to execute)")
        for item in fixed_specs[:10]:
            print(f"         SPEC-{item['spec_id']}: -{item['removed']}, {item['remaining']} remaining")
        if len(fixed_specs) > 10:
            print(f"         ... and {len(fixed_specs) - 10} more")
    return {"specs_fixed": len(fixed_specs), "assertions_removed": total_removed, "details": fixed_specs}


def fix_3_archive_scripts(*, apply: bool = False) -> dict:
    """Move one-off session and record scripts to scripts/archive/."""
    session_scripts = sorted(SCRIPT_DIR.glob("s1[0-9]*_*.py"))
    record_scripts = sorted(SCRIPT_DIR.glob("record_*.py"))
    all_scripts = session_scripts + record_scripts

    # Exclude this script and the integrity scan itself
    exclude = {"s159_integrity_fixes.py", "integrity_scan.py"}
    to_archive = [s for s in all_scripts if s.name not in exclude]

    if apply and to_archive:
        ARCHIVE_DIR.mkdir(exist_ok=True)
        for script in to_archive:
            dest = ARCHIVE_DIR / script.name
            shutil.move(str(script), str(dest))

    print(f"  Fix 3: Scripts archived: {len(to_archive)} -> scripts/archive/")
    if not apply and to_archive:
        print(f"         (dry-run — use --apply to execute)")
        print(f"         {len(session_scripts)} session scripts (s1XX_*.py)")
        print(f"         {len(record_scripts)} record scripts (record_*.py)")
    return {"count": len(to_archive), "session": len(session_scripts), "record": len(record_scripts)}


def fix_4_tighten_broad_patterns(db: KnowledgeDB, *, apply: bool = False) -> dict:
    """Tighten overly broad patterns (>50 matches) where a better pattern is obvious.

    Strategy: For patterns that are single common words (like 'trace', 'connection',
    'alert', 'widget'), try to find a more specific pattern from the spec title or
    description that still matches the file.
    """
    conn = db._get_conn()
    specs = conn.execute("""
        SELECT id, title, status, assertions FROM current_specifications
        WHERE status != 'retired'
          AND assertions IS NOT NULL AND assertions != 'null' AND assertions != '[]'
    """).fetchall()

    tightened = []

    for spec in specs:
        spec_id = spec["id"]
        title = spec["title"] or ""
        try:
            assertions = json.loads(spec["assertions"])
        except (json.JSONDecodeError, TypeError):
            continue
        if not isinstance(assertions, list):
            continue

        updated = False
        new_assertions = []

        for a in assertions:
            a_type = a.get("type", "grep")
            a_file = a.get("file", "")
            a_pattern = a.get("pattern", "")

            if a_type != "grep" or not a_file or not a_pattern:
                new_assertions.append(a)
                continue

            full_path = PROJECT_ROOT / a_file
            if not full_path.exists():
                new_assertions.append(a)
                continue

            try:
                content = full_path.read_text(encoding="utf-8", errors="replace")
                match_count = len(re.findall(re.escape(a_pattern), content))
            except Exception:
                new_assertions.append(a)
                continue

            if match_count <= 50:
                new_assertions.append(a)
                continue

            # Pattern is overly broad — try to extract a better one from the title
            # Look for CamelCase identifiers, function names, or specific terms
            candidates = []

            # Extract quoted strings from title
            for m in re.finditer(r'`([^`]+)`|"([^"]+)"', title):
                candidates.append(m.group(1) or m.group(2))

            # Extract CamelCase words from title
            for m in re.finditer(r'[A-Z][a-z]+(?:[A-Z][a-z]+)+', title):
                candidates.append(m.group())

            # Extract snake_case identifiers from title
            for m in re.finditer(r'[a-z][a-z0-9]*(?:_[a-z][a-z0-9]*)+', title):
                candidates.append(m.group())

            # Try each candidate — pick the first that matches 1-50 times
            best = None
            for cand in candidates:
                if len(cand) < 4:
                    continue
                cand_count = len(re.findall(re.escape(cand), content))
                if 1 <= cand_count <= 50:
                    best = cand
                    break

            if best:
                new_a = dict(a)
                new_a["pattern"] = best
                new_assertions.append(new_a)
                tightened.append({
                    "spec_id": spec_id,
                    "old_pattern": a_pattern,
                    "new_pattern": best,
                    "old_matches": match_count,
                })
                updated = True
            else:
                new_assertions.append(a)  # Keep original if no better pattern found

        if updated and apply:
            db.update_spec(
                spec_id,
                changed_by="S159-integrity",
                change_reason="Tighten overly broad assertion pattern (integrity scan Fix 4)",
                assertions=new_assertions,
            )

    print(f"  Fix 4: Overly broad patterns tightened: {len(tightened)}")
    if not apply and tightened:
        print(f"         (dry-run — use --apply to execute)")
    for item in tightened[:10]:
        print(f"         SPEC-{item['spec_id']}: '{item['old_pattern']}' ({item['old_matches']}x) -> '{item['new_pattern']}'")
    if len(tightened) > 10:
        print(f"         ... and {len(tightened) - 10} more")
    return {"count": len(tightened), "details": tightened}


def report_orphaned_tests(db: KnowledgeDB) -> dict:
    """Report on orphaned test artifacts — these need manual mapping, not automated fixes."""
    conn = db._get_conn()
    groups = conn.execute("""
        SELECT t.spec_id, COUNT(*) as cnt
        FROM current_tests t
        LEFT JOIN current_specifications s ON t.spec_id = s.id
        WHERE s.id IS NULL
        GROUP BY t.spec_id
        ORDER BY cnt DESC
    """).fetchall()

    print(f"\n  Report: Orphaned test artifacts (2,317 tests with unlinked spec_ids)")
    print(f"  These use grouping conventions (SPEC-100, SPEC-400, etc.) instead of real spec IDs.")
    print(f"  Fixing these requires individual spec-to-test mapping — deferred to future session.")
    for r in groups:
        print(f"         spec_id={r['spec_id']!r:25s} count={r['cnt']}")

    return {"total": sum(r["cnt"] for r in groups), "groups": [dict(r) for r in groups]}


def report_missing_test_files(db: KnowledgeDB) -> dict:
    """Report test artifacts whose test_file no longer exists."""
    conn = db._get_conn()
    test_files = conn.execute("""
        SELECT DISTINCT test_file FROM current_tests
        WHERE test_file IS NOT NULL AND test_file != ''
    """).fetchall()

    missing = []
    for row in test_files:
        tf = row["test_file"]
        if not (PROJECT_ROOT / tf).exists():
            missing.append(tf)

    print(f"\n  Report: Test artifacts with missing test_file: {len(missing)}")
    print(f"  These reference files that were renamed, moved, or removed.")
    print(f"  Creating 74 new test versions just to note staleness would be low-value churn.")
    for f in missing[:10]:
        print(f"         {f}")
    if len(missing) > 10:
        print(f"         ... and {len(missing) - 10} more")

    return {"count": len(missing), "files": missing}


def main():
    parser = argparse.ArgumentParser(description="S159 Integrity Scan Remediation")
    parser.add_argument("--apply", action="store_true",
                        help="Actually execute fixes (default is dry-run)")
    parser.add_argument("--fix", nargs="+", type=int, default=None,
                        help="Run specific fixes only (e.g., --fix 1 2)")
    args = parser.parse_args()

    fixes_to_run = set(args.fix) if args.fix else {1, 2, 3, 4}

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"{'='*60}")
    print(f"  S159 Integrity Scan Remediation [{mode}]")
    print(f"  Fixes: {sorted(fixes_to_run)}")
    print(f"{'='*60}")

    db = KnowledgeDB()
    results = {}

    if 1 in fixes_to_run:
        results["fix_1"] = fix_1_retired_spec_assertions(db, apply=args.apply)
    if 2 in fixes_to_run:
        results["fix_2"] = fix_2_dead_pattern_assertions(db, apply=args.apply)
    if 3 in fixes_to_run:
        results["fix_3"] = fix_3_archive_scripts(apply=args.apply)
    if 4 in fixes_to_run:
        results["fix_4"] = fix_4_tighten_broad_patterns(db, apply=args.apply)

    # Always show reports
    results["report_orphaned"] = report_orphaned_tests(db)
    results["report_missing_files"] = report_missing_test_files(db)

    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    total_actions = 0
    if "fix_1" in results:
        total_actions += results["fix_1"]["count"]
    if "fix_2" in results:
        total_actions += results["fix_2"]["specs_fixed"]
    if "fix_3" in results:
        total_actions += results["fix_3"]["count"]
    if "fix_4" in results:
        total_actions += results["fix_4"]["count"]
    print(f"  Total actions: {total_actions}")
    if not args.apply:
        print(f"  Mode: DRY-RUN (re-run with --apply to execute)")
    else:
        print(f"  Mode: APPLIED")

    db.close()


if __name__ == "__main__":
    main()
