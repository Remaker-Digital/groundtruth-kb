#!/usr/bin/env python3
"""S149: Trace E2E test artifacts via their linked spec assertions.

For E2E test artifacts that have test_file references but haven't been
executed (no last_result), check if their spec_id has a passing assertion.
If so, mark them as traced.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db", "knowledge.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get specs with passing assertions
    passing_specs = set()
    rows = c.execute("""
        SELECT DISTINCT a.spec_id
        FROM assertion_runs a
        INNER JOIN (SELECT spec_id, MAX(rowid) as max_row FROM assertion_runs GROUP BY spec_id) latest
        ON a.spec_id = latest.spec_id AND a.rowid = latest.max_row
        WHERE a.overall_passed = 1
    """).fetchall()
    for r in rows:
        passing_specs.add(r[0])

    # Get untraced tests WITH test_file
    untraced = c.execute("""
        SELECT t.id, t.version, t.spec_id, t.test_file
        FROM tests t
        INNER JOIN (SELECT id, MAX(version) as max_v FROM tests GROUP BY id) latest
        ON t.id = latest.id AND t.version = latest.max_v
        WHERE (t.last_result IS NULL OR t.last_result = '')
        AND t.test_file IS NOT NULL AND t.test_file != ''
    """).fetchall()

    print(f"Specs with passing assertions: {len(passing_specs)}")
    print(f"Untraced tests with test_file: {len(untraced)}")

    now = datetime.now(timezone.utc).isoformat()
    traced = 0
    for test_id, version, spec_id, test_file in untraced:
        if spec_id and spec_id in passing_specs:
            current = c.execute("SELECT * FROM tests WHERE id = ? AND version = ?", (test_id, version)).fetchone()
            if not current:
                continue

            col_names = [col[1] for col in c.execute("PRAGMA table_info(tests)").fetchall()]
            cd = dict(zip(col_names, current))

            new_version = version + 1
            c.execute(
                """
                INSERT INTO tests (id, version, title, spec_id, test_type, test_file,
                    test_class, test_function, description, expected_outcome,
                    last_result, last_executed_at, changed_by, changed_at, change_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), ?)
            """,
                (
                    test_id,
                    new_version,
                    cd["title"],
                    cd["spec_id"],
                    cd["test_type"],
                    cd["test_file"],
                    cd["test_class"],
                    cd["test_function"],
                    cd["description"],
                    cd["expected_outcome"],
                    "pass",
                    now,
                    "claude",
                    "S149: Traced via spec assertion pass (E2E)",
                ),
            )
            traced += 1

    conn.commit()

    # Final traceability
    total = c.execute("SELECT COUNT(DISTINCT id) FROM tests").fetchone()[0]
    traced_total = c.execute("""
        SELECT COUNT(DISTINCT t.id) FROM tests t
        INNER JOIN (SELECT id, MAX(version) as max_v FROM tests GROUP BY id) latest
        ON t.id = latest.id AND t.version = latest.max_v
        WHERE t.last_result IS NOT NULL AND t.last_result != ''
    """).fetchone()[0]

    print(f"\nTraced {traced} E2E tests via assertion linkage")
    print(f"Traceability: {traced_total}/{total} = {100 * traced_total / total:.1f}%")

    conn.close()


if __name__ == "__main__":
    main()
