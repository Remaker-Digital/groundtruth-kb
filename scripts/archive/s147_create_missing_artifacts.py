#!/usr/bin/env python3
"""S147: Create KB test artifacts for pytest tests that don't have KB entries.

Parses JUnit XML files and creates KB test artifacts for any test case
that doesn't already have a matching (test_file, test_function) entry.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "tools" / "knowledge-db"))
from db import KnowledgeDB


def _classname_to_filepath(classname: str) -> str:
    """Convert JUnit classname (dots) to file path (slashes)."""
    parts = classname.split(".")
    module_parts = []
    for part in parts:
        if part and part[0].isupper():
            break
        module_parts.append(part)
    return "/".join(module_parts) + ".py" if module_parts else ""


def _classify_test_type(filepath: str) -> str:
    """Determine test type from file path."""
    if "e2e_live" in filepath:
        return "e2e"
    if "e2e" in filepath:
        return "e2e"
    if "security" in filepath:
        return "security"
    if "integration" in filepath or "integrations" in filepath:
        return "integration"
    if "performance" in filepath:
        return "performance"
    if "evaluation" in filepath:
        return "e2e"
    if "visual" in filepath:
        return "e2e"
    if "ops" in filepath:
        return "integration"
    if "migration" in filepath:
        return "integration"
    return "unit"


def main():
    dry_run = "--dry-run" in sys.argv
    xml_files = []
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            continue
        xml_files.append(arg)

    if not xml_files:
        print("Usage: python s147_create_missing_artifacts.py <xml1> [xml2 ...] [--dry-run]")
        sys.exit(1)

    k = KnowledgeDB()
    conn = k._conn

    # Build set of existing (test_file, test_function) pairs
    cur = conn.execute("SELECT test_file, test_function FROM current_tests WHERE test_file IS NOT NULL")
    existing = set()
    for row in cur.fetchall():
        existing.add((row[0], row[1]))
    print(f"Existing KB artifacts: {len(existing)} unique (file, function) pairs")

    # Get next test ID
    cur = conn.execute("SELECT id FROM tests ORDER BY rowid DESC LIMIT 1")
    last = cur.fetchone()
    last_num = int(last[0].replace("TEST-", "")) if last else 0
    next_num = last_num + 1

    # Process all XML files
    created = 0
    skipped = 0
    now = datetime.now(timezone.utc).isoformat()

    for xml_path in xml_files:
        p = Path(xml_path)
        if not p.exists():
            print(f"  SKIP: {xml_path} not found")
            continue

        tree = ET.parse(str(p))
        root = tree.getroot()
        cases = root.findall(".//testcase")
        print(f"\nProcessing {xml_path}: {len(cases)} test cases")

        for tc in cases:
            classname = tc.get("classname", "")
            name = tc.get("name", "")
            file_path = _classname_to_filepath(classname)

            if not file_path or not name:
                skipped += 1
                continue

            if (file_path, name) in existing:
                skipped += 1
                continue

            # Determine result
            result = "pass"
            if tc.find("failure") is not None:
                result = "fail"
            elif tc.find("error") is not None:
                result = "fail"
            elif tc.find("skipped") is not None:
                result = "skip"

            # Extract class name
            test_class = None
            parts = classname.split(".")
            for part in parts:
                if part and part[0].isupper():
                    test_class = part
                    break

            test_id = f"TEST-{next_num:04d}"
            test_type = _classify_test_type(file_path)

            if not dry_run:
                k.insert_test(
                    id=test_id,
                    title=f"{test_class}.{name}" if test_class else name,
                    test_type=test_type,
                    spec_id="",
                    expected_outcome="pass",
                    changed_by="S147 auto-create",
                    change_reason="Batch artifact creation for traceability",
                    test_file=file_path,
                    test_class=test_class,
                    test_function=name,
                    description=f"Auto-created from JUnit XML ({file_path})",
                    last_result=result,
                    last_executed_at=now,
                )

            existing.add((file_path, name))
            created += 1
            next_num += 1

    print(f"\nCreated: {created} new KB artifacts")
    print(f"Skipped: {skipped} (already exist or invalid)")

    # Final traceability
    cur = conn.execute("SELECT COUNT(*) FROM current_tests")
    total = cur.fetchone()[0]
    cur = conn.execute("SELECT COUNT(*) FROM current_tests WHERE last_result IS NOT NULL AND last_result != ''")
    traced = cur.fetchone()[0]
    print(f"Test Traceability: {traced}/{total} ({traced / total * 100:.1f}%)")

    k.close()


if __name__ == "__main__":
    main()
