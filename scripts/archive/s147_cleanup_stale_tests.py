#!/usr/bin/env python3
"""S147: Identify and mark stale KB test artifacts.

Finds KB test artifacts whose test_file exists but test_function is missing
from the actual file. Marks these with last_result='STALE' so they don't
drag down traceability metrics.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import ast
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "tools" / "knowledge-db"))
from db import KnowledgeDB


def main():
    dry_run = "--dry-run" in sys.argv
    k = KnowledgeDB()
    conn = k._conn

    # Find untraced artifacts with valid test_file
    cur = conn.execute("""
        SELECT id, test_file, test_function, version
        FROM current_tests
        WHERE (last_result IS NULL OR last_result = '')
        AND test_file IS NOT NULL AND test_file != ''
    """)
    rows = cur.fetchall()
    print(f"Untraced artifacts with test_file: {len(rows)}")

    # Cache parsed ASTs
    ast_cache: dict[str, set[str] | None] = {}

    stale = []
    valid = []
    missing_file = []
    now = datetime.now(timezone.utc).isoformat()

    for row in rows:
        test_id = row[0]
        test_file = row[1]
        test_func = row[2]
        version = row[3]

        if test_file not in ast_cache:
            p = PROJECT_DIR / test_file
            if p.exists():
                try:
                    tree = ast.parse(p.read_text())
                    funcs = {
                        n.name
                        for n in ast.walk(tree)
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    }
                    ast_cache[test_file] = funcs
                except Exception:
                    ast_cache[test_file] = None
            else:
                ast_cache[test_file] = None

        funcs = ast_cache.get(test_file)
        if funcs is None:
            missing_file.append((test_id, test_file, test_func))
        elif test_func not in funcs:
            stale.append((test_id, test_file, test_func, version))
        else:
            valid.append((test_id, test_file, test_func))

    print(f"  Stale (file exists, func missing): {len(stale)}")
    print(f"  Missing file: {len(missing_file)}")
    print(f"  Valid (func exists, not yet traced): {len(valid)}")

    if stale and not dry_run:
        # Mark stale artifacts so they're excluded from traceability gap
        for test_id, tf, fn, ver in stale:
            conn.execute(
                """UPDATE tests SET last_result = 'STALE', last_executed_at = ?
                   WHERE id = ? AND version = ?""",
                (now, test_id, ver),
            )
        conn.commit()
        print(f"  Marked {len(stale)} artifacts as STALE")

    if missing_file and not dry_run:
        for test_id, tf, fn in missing_file:
            conn.execute(
                """UPDATE tests SET last_result = 'STALE', last_executed_at = ?
                   WHERE id = ? AND version = (SELECT MAX(version) FROM tests WHERE id = ?)""",
                (now, test_id, test_id),
            )
        conn.commit()
        print(f"  Marked {len(missing_file)} missing-file artifacts as STALE")

    # Final traceability
    cur = conn.execute("SELECT COUNT(*) FROM current_tests")
    total = cur.fetchone()[0]
    cur = conn.execute(
        "SELECT COUNT(*) FROM current_tests WHERE last_result IS NOT NULL AND last_result != ''"
    )
    traced = cur.fetchone()[0]
    print(f"\nTest Traceability: {traced}/{total} ({traced / total * 100:.1f}%)")

    # Show sample stale
    if stale:
        print("\nSample stale artifacts:")
        for test_id, tf, fn, ver in stale[:10]:
            print(f"  {test_id}: {tf}::{fn}")

    k.close()


if __name__ == "__main__":
    main()
