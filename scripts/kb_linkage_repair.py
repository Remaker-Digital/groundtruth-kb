"""
KB Linkage Repair Script — S218
Fixes test-to-spec linkage issues identified by Codex KB re-audit.

Phase 1: Fix 66 test records with class-encoded-as-path test_file values
Phase 2: Link 19 implemented specs that have test files but no KB test records
Phase 3: Fix 27 truly missing test_file paths (deleted/renamed test files)
Phase 4: Report on orphaned placeholder spec IDs (SPEC-100, SPEC-400, etc.)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sqlite3
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

sys.path.insert(0, str(PROJECT_ROOT / "tools" / "knowledge-db"))
import db as kbmod

DB_PATH = PROJECT_ROOT / "groundtruth.db"
REPO = PROJECT_ROOT
DRY_RUN = "--dry-run" in sys.argv
CHANGED_BY = "S218-linkage-repair"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def phase1_fix_class_as_path():
    """Fix test records where test_class was encoded as a subdirectory in test_file."""
    print("=" * 70)
    print("PHASE 1: Fix class-as-path test_file encoding")
    print("=" * 70)

    conn = get_conn()
    cur = conn.cursor()

    # Find all missing test_file paths
    cur.execute(
        'SELECT DISTINCT test_file FROM current_tests '
        'WHERE test_file IS NOT NULL AND test_file != ""'
    )
    all_paths = [r[0] for r in cur.fetchall()]

    fixes = {}  # old_path -> (new_path, class_name)
    for p in all_paths:
        if (REPO / p).exists():
            continue
        parts = Path(p).parts
        if len(parts) >= 3:
            parent_as_file = Path(*parts[:-1]).with_suffix(".py")
            if (REPO / parent_as_file).exists():
                class_name = Path(p).stem
                fixes[p] = (str(parent_as_file).replace("\\", "/"), class_name)

    print(f"  Found {len(fixes)} class-as-path encodings to fix")

    # Use the KB API to create new test versions with corrected paths
    kb = kbmod.KnowledgeDB()
    fixed_count = 0

    for old_path, (new_path, class_name) in fixes.items():
        # Get all test records with this path
        cur.execute(
            "SELECT * FROM current_tests WHERE test_file = ?", (old_path,)
        )
        tests = cur.fetchall()

        for test in tests:
            test_id = test["id"]
            if DRY_RUN:
                print(f"  [DRY RUN] Would fix {test_id}: {old_path} -> {new_path} (class={class_name})")
            else:
                kb.insert_test(
                    id=test_id,
                    title=test["title"],
                    spec_id=test["spec_id"],
                    test_type=test["test_type"],
                    expected_outcome=test["expected_outcome"],
                    changed_by=CHANGED_BY,
                    change_reason=f"Fix class-as-path encoding: {old_path} -> {new_path}",
                    test_file=new_path,
                    test_class=class_name,
                    test_function=test["test_function"],
                    description=test["description"],
                    last_result=test["last_result"],
                    last_executed_at=test["last_executed_at"],
                )
                fixed_count += 1

    print(f"  Fixed: {fixed_count} test records")
    return fixed_count


def phase2_link_unlinked_specs():
    """Create test records for 19 specs that have test files but no KB linkage."""
    print()
    print("=" * 70)
    print("PHASE 2: Link implemented specs to existing test files")
    print("=" * 70)

    conn = get_conn()
    cur = conn.cursor()

    # Get implemented specs with no tests
    cur.execute('''
        SELECT id, title FROM current_specifications
        WHERE status = 'implemented'
        AND id NOT IN (SELECT DISTINCT spec_id FROM current_tests)
    ''')
    no_test_specs = cur.fetchall()

    test_files = list(REPO.glob("tests/**/*.py"))
    kb = kbmod.KnowledgeDB()
    linked_count = 0

    # Get next test ID
    cur.execute("SELECT MAX(CAST(SUBSTR(id, 6) AS INTEGER)) FROM current_tests WHERE id LIKE 'TEST-%'")
    row = cur.fetchone()
    next_test_num = (row[0] or 0) + 1

    for spec in no_test_specs:
        spec_id = spec["id"]
        spec_title = spec["title"]

        # Find test files that reference this spec
        matching_files = []
        for tf in test_files:
            try:
                content = tf.read_text(encoding="utf-8", errors="ignore")
                if spec_id in content:
                    matching_files.append(tf)
            except Exception:
                pass

        if not matching_files:
            continue

        for tf in matching_files:
            rel_path = str(tf.relative_to(REPO)).replace("\\", "/")
            test_id = f"TEST-{next_test_num:05d}"
            next_test_num += 1

            if DRY_RUN:
                print(f"  [DRY RUN] Would create {test_id} linking {spec_id} -> {rel_path}")
            else:
                kb.insert_test(
                    id=test_id,
                    title=f"Linkage: {spec_title[:60]}",
                    spec_id=spec_id,
                    test_type="integration",
                    expected_outcome=f"Tests in {rel_path} verify {spec_id} requirements",
                    changed_by=CHANGED_BY,
                    change_reason=f"KB linkage repair: connect {spec_id} to existing test file",
                    test_file=rel_path,
                )
                linked_count += 1
                print(f"  Created {test_id}: {spec_id} -> {rel_path}")

    print(f"  Linked: {linked_count} new test records")
    return linked_count


def phase3_fix_missing_paths():
    """Clear test_file for tests pointing to deleted/renamed files."""
    print()
    print("=" * 70)
    print("PHASE 3: Fix truly missing test_file paths")
    print("=" * 70)

    conn = get_conn()
    cur = conn.cursor()

    # Get all distinct missing paths that aren't class-as-path fixable
    cur.execute(
        'SELECT DISTINCT test_file FROM current_tests '
        'WHERE test_file IS NOT NULL AND test_file != ""'
    )
    all_paths = [r[0] for r in cur.fetchall()]

    truly_missing = []
    for p in all_paths:
        if (REPO / p).exists():
            continue
        # Check if it's a class-as-path (already fixed in phase 1)
        parts = Path(p).parts
        if len(parts) >= 3:
            parent_as_file = Path(*parts[:-1]).with_suffix(".py")
            if (REPO / parent_as_file).exists():
                continue  # Already fixed
        # Check simple rename
        fname = Path(p).name
        matches = list(REPO.glob(f"tests/**/{fname}"))
        if matches:
            truly_missing.append((p, str(matches[0].relative_to(REPO)).replace("\\", "/")))
        else:
            truly_missing.append((p, None))

    kb = kbmod.KnowledgeDB()
    fixed_count = 0

    for old_path, new_path in truly_missing:
        cur.execute("SELECT * FROM current_tests WHERE test_file = ?", (old_path,))
        tests = cur.fetchall()

        for test in tests:
            test_id = test["id"]
            if new_path:
                reason = f"Path correction: {old_path} -> {new_path}"
                file_val = new_path
            else:
                reason = f"Cleared stale test_file: {old_path} (file deleted/renamed)"
                file_val = None

            if DRY_RUN:
                print(f"  [DRY RUN] {test_id}: {old_path} -> {new_path or 'CLEARED'}")
            else:
                kb.insert_test(
                    id=test_id,
                    title=test["title"],
                    spec_id=test["spec_id"],
                    test_type=test["test_type"],
                    expected_outcome=test["expected_outcome"],
                    changed_by=CHANGED_BY,
                    change_reason=reason,
                    test_file=file_val,
                    test_class=test["test_class"],
                    test_function=test["test_function"],
                    description=test["description"],
                    last_result=test["last_result"],
                    last_executed_at=test["last_executed_at"],
                )
                fixed_count += 1

    print(f"  Fixed: {fixed_count} test records ({len(truly_missing)} distinct paths)")
    return fixed_count


def phase4_report_orphaned_spec_ids():
    """Report on orphaned placeholder spec IDs — analysis only, no changes."""
    print()
    print("=" * 70)
    print("PHASE 4: Orphaned placeholder spec IDs (report only)")
    print("=" * 70)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute('''
        SELECT spec_id, COUNT(*) as cnt
        FROM current_tests
        WHERE spec_id NOT IN (SELECT id FROM current_specifications)
        GROUP BY spec_id
        ORDER BY cnt DESC
    ''')
    rows = cur.fetchall()

    total_orphaned = sum(r["cnt"] for r in rows)
    print(f"  Total orphaned test rows: {total_orphaned}")
    print(f"  Distinct orphaned spec IDs: {len(rows)}")
    print()
    print("  Top orphaned IDs:")
    for r in rows[:10]:
        print(f"    {r['spec_id']}: {r['cnt']} tests")

    # Analyze what the placeholder IDs contain
    for placeholder in ["SPEC-100", "SPEC-400", "SPEC-general", "SPEC-700", "SPEC-500"]:
        cur.execute(
            "SELECT DISTINCT test_file FROM current_tests WHERE spec_id = ? AND test_file IS NOT NULL AND test_file != ''",
            (placeholder,),
        )
        files = [r[0] for r in cur.fetchall()]
        print(f"\n  {placeholder} test files ({len(files)}):")
        for f in sorted(files)[:5]:
            print(f"    {f}")
        if len(files) > 5:
            print(f"    ... and {len(files) - 5} more")

    return total_orphaned


def main():
    mode = "DRY RUN" if DRY_RUN else "LIVE"
    print(f"\n{'#' * 70}")
    print(f"  KB LINKAGE REPAIR — S218 ({mode})")
    print(f"{'#' * 70}\n")

    p1 = phase1_fix_class_as_path()
    p2 = phase2_link_unlinked_specs()
    p3 = phase3_fix_missing_paths()
    p4 = phase4_report_orphaned_spec_ids()

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Phase 1 (class-as-path fix): {p1} records")
    print(f"  Phase 2 (spec linkage):      {p2} records")
    print(f"  Phase 3 (missing path fix):  {p3} records")
    print(f"  Phase 4 (orphaned IDs):      {p4} orphaned (report only)")
    print()
    if DRY_RUN:
        print("  ** DRY RUN — no changes made. Remove --dry-run to apply. **")


if __name__ == "__main__":
    main()
