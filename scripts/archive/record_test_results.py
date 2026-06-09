#!/usr/bin/env python3
"""
Record pytest results into the Knowledge Database test artifacts.

Parses JUnit XML output from pytest and matches each test case to KB test
artifacts via test_file + test_function fields. Updates matched artifacts
with last_result and last_executed_at.

Usage:
    python scripts/record_test_results.py --xml logs/test-results.xml
    python scripts/record_test_results.py --xml logs/test-results.xml --dry-run

Implements SPEC-1661 (Test Traceability Automation).

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
KB_DIR = PROJECT_DIR / "tools" / "knowledge-db"


def _parse_junit_xml(xml_path: str) -> list[dict]:
    """Parse JUnit XML and extract test case results.

    Returns list of dicts with keys:
        file, classname, function, result (pass|fail|skip|error), duration
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    cases = []
    # JUnit XML structure: <testsuites><testsuite><testcase ...>
    for tc in root.iter("testcase"):
        classname = tc.get("classname", "")
        name = tc.get("name", "")
        time_val = float(tc.get("time", "0"))

        # Determine result
        if tc.find("failure") is not None:
            result = "fail"
        elif tc.find("error") is not None:
            result = "error"
        elif tc.find("skipped") is not None:
            result = "skip"
        else:
            result = "pass"

        # Derive file path from classname (pytest convention: dots → slashes)
        # e.g. "tests.unit.test_foo" → "tests/unit/test_foo.py"
        file_path = ""
        if classname:
            # Split on dots — last part may be the class or the module
            parts = classname.split(".")
            # pytest JUnit XML classname format varies:
            #   - tests.unit.test_foo.TestClass → file is tests/unit/test_foo.py
            #   - tests.unit.test_foo → file is tests/unit/test_foo.py
            # We need to find where the module ends and class begins.
            # Heuristic: module parts start lowercase, class starts uppercase.
            module_parts = []
            class_name = None
            for i, part in enumerate(parts):
                if part and part[0].isupper() and i > 0:
                    class_name = part
                    break
                module_parts.append(part)

            if module_parts:
                file_path = "/".join(module_parts) + ".py"

        cases.append(
            {
                "file": file_path,
                "classname": classname,
                "class": class_name if "class_name" in dir() and class_name else None,
                "function": name,
                "result": result,
                "duration": time_val,
            }
        )

    return cases


def _build_kb_index(db) -> dict[tuple[str, str], list[dict]]:
    """Build an index of KB test artifacts by (test_file, test_function).

    Returns dict mapping (file, function) → list of KB test records.
    Multiple KB artifacts can map to the same pytest test.
    """
    conn = db._get_conn()
    rows = conn.execute(
        """SELECT id, test_file, test_class, test_function, last_result
           FROM current_tests
           WHERE test_file IS NOT NULL AND test_file != ''
             AND test_function IS NOT NULL AND test_function != ''"""
    ).fetchall()

    index: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        key = (r["test_file"], r["test_function"])
        entry = {
            "id": r["id"],
            "test_class": r["test_class"],
            "last_result": r["last_result"],
        }
        index.setdefault(key, []).append(entry)

    return index


def main():
    parser = argparse.ArgumentParser(description="Record pytest results into KB test artifacts (SPEC-1661)")
    parser.add_argument("--xml", required=True, help="Path to JUnit XML file from pytest --junitxml")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")
    args = parser.parse_args()

    xml_path = args.xml
    if not os.path.exists(xml_path):
        print(f"ERROR: XML file not found: {xml_path}")
        sys.exit(1)

    # Parse JUnit XML
    print(f"Parsing {xml_path}...")
    cases = _parse_junit_xml(xml_path)
    print(f"  Found {len(cases)} test cases in XML")

    result_counts = {}
    for c in cases:
        result_counts[c["result"]] = result_counts.get(c["result"], 0) + 1
    print(f"  Results: {result_counts}")

    # Connect to KB
    sys.path.insert(0, str(KB_DIR))
    from db import KnowledgeDB

    db_path = KB_DIR / "knowledge.db"
    if not db_path.exists():
        print(f"ERROR: KB database not found: {db_path}")
        sys.exit(1)

    db = KnowledgeDB(str(db_path))
    try:
        # Build KB index
        print("Building KB test artifact index...")
        kb_index = _build_kb_index(db)
        print(
            f"  Indexed {len(kb_index)} unique (file, function) pairs "
            f"from {sum(len(v) for v in kb_index.values())} KB artifacts"
        )

        # Match and update
        now = datetime.now(timezone.utc).isoformat()
        matched = 0
        updated = 0
        skipped_unchanged = 0
        unmatched = 0
        multi_match = 0

        for case in cases:
            file_key = case["file"]
            func_key = case["function"]

            # Try exact match
            kb_entries = kb_index.get((file_key, func_key))

            # Fallback: strip parametrize brackets (e.g. "test_foo[param]" -> "test_foo")
            if not kb_entries and "[" in func_key:
                base_func = func_key.split("[")[0]
                kb_entries = kb_index.get((file_key, base_func))

            if not kb_entries:
                unmatched += 1
                continue

            matched += 1
            if len(kb_entries) > 1:
                multi_match += 1

            # Map pytest result to KB result format
            kb_result = case["result"]  # pass, fail, skip, error

            for entry in kb_entries:
                # Skip if result hasn't changed
                if entry["last_result"] == kb_result:
                    skipped_unchanged += 1
                    continue

                if args.dry_run:
                    print(f"  [DRY RUN] Would update {entry['id']}: {entry['last_result']} → {kb_result}")
                    updated += 1
                else:
                    db.update_test(
                        entry["id"],
                        changed_by="test-results-recorder",
                        change_reason=f"Automated: pytest result recorded ({kb_result})",
                        last_result=kb_result,
                        last_executed_at=now,
                    )
                    updated += 1

        # Report
        print()
        print("=" * 50)
        print(f"  Test Results Recording {'(DRY RUN) ' if args.dry_run else ''}Summary")
        print("=" * 50)
        print(f"  XML test cases:     {len(cases)}")
        print(f"  KB artifacts matched: {matched}")
        print(f"  KB artifacts updated: {updated}")
        print(f"  Unchanged (same result): {skipped_unchanged}")
        print(f"  Multi-match cases:  {multi_match}")
        print(f"  Unmatched (no KB entry): {unmatched}")
        print("=" * 50)

        # Show traceability improvement
        conn = db._get_conn()
        trace_row = conn.execute(
            """SELECT COUNT(*) AS total,
                      SUM(CASE WHEN last_result IS NOT NULL THEN 1 ELSE 0 END) AS traced
               FROM current_tests"""
        ).fetchone()
        total = trace_row["total"] or 0
        traced = trace_row["traced"] or 0
        pct = (traced / total * 100) if total else 0
        print(f"  Test Traceability: {traced}/{total} ({pct:.1f}%)")

    finally:
        db.close()


if __name__ == "__main__":
    main()
