#!/usr/bin/env python3
"""S147: Batch-create KB test artifacts for unmatched pytest tests.

Parses JUnit XML results and creates KB test artifacts for tests that
don't yet have entries, improving test traceability toward the 80% target.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "tools" / "knowledge-db"))
from db import KnowledgeDB

# Directory → test_type mapping
DIR_TYPE_MAP = {
    "tests/unit": "unit",
    "tests/multi_tenant": "unit",
    "tests/agents": "unit",
    "tests/integrations": "integration",
    "tests/widget": "unit",
    "tests/e2e": "e2e",
    "tests/e2e_live": "e2e",
    "tests/security": "security",
    "tests/chat": "unit",
    "tests/performance": "performance",
    "tests/ops": "operational",
    "tests/live_api": "integration",
    "tests/regression": "regression",
    "tests/evaluation": "evaluation",
    "tests/persistent_memory": "unit",
    "tests/visual": "visual",
    "tests/migrations": "unit",
    "tests/hooks": "unit",
    "tests/integration": "integration",
}

# Directory → spec_id mapping (best-effort, general specs)
DIR_SPEC_MAP = {
    "tests/unit": "SPEC-100",
    "tests/multi_tenant": "SPEC-1100",
    "tests/agents": "SPEC-500",
    "tests/integrations": "SPEC-700",
    "tests/widget": "SPEC-400",
    "tests/chat": "SPEC-600",
    "tests/security": "SPEC-800",
}


def parse_junit_xml(xml_path: str) -> list[dict]:
    """Parse JUnit XML and extract test cases."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    cases = []
    for tc in root.iter("testcase"):
        classname = tc.get("classname", "")
        name = tc.get("name", "")
        time_val = float(tc.get("time", "0"))
        if tc.find("failure") is not None:
            result = "fail"
        elif tc.find("error") is not None:
            result = "error"
        elif tc.find("skipped") is not None:
            result = "skip"
        else:
            result = "pass"
        # Derive file path
        parts = classname.split(".")
        module_parts = []
        class_name = None
        for i, part in enumerate(parts):
            if part and part[0].isupper() and i > 0:
                class_name = part
                break
            module_parts.append(part)
        file_path = "/".join(module_parts) + ".py" if module_parts else ""
        cases.append(
            {
                "file": file_path,
                "classname": classname,
                "class": class_name,
                "function": name,
                "result": result,
                "duration": time_val,
            }
        )
    return cases


def get_test_type(file_path: str) -> str:
    """Map file path to test type."""
    for prefix, ttype in DIR_TYPE_MAP.items():
        if file_path.startswith(prefix):
            return ttype
    return "unit"


def get_spec_id(file_path: str) -> str:
    """Best-effort spec_id from directory."""
    for prefix, sid in DIR_SPEC_MAP.items():
        if file_path.startswith(prefix):
            return sid
    return "SPEC-100"


def humanize_test_name(function_name: str) -> str:
    """Convert test_function_name to a readable title."""
    name = function_name
    if name.startswith("test_"):
        name = name[5:]
    # Replace underscores with spaces and title-case
    return name.replace("_", " ").strip()


def main():
    dry_run = "--dry-run" in sys.argv

    xml_dir = PROJECT_DIR / "tests" / "results"
    xml_files = sorted(xml_dir.glob("*-results.xml"))
    if not xml_files:
        print("ERROR: No JUnit XML files found in tests/results/")
        sys.exit(1)

    print(f"Found {len(xml_files)} XML files:")
    for f in xml_files:
        print(f"  {f.name}")

    # Parse all XML files
    all_cases = []
    for xf in xml_files:
        cases = parse_junit_xml(str(xf))
        all_cases.extend(cases)
        print(f"  {xf.name}: {len(cases)} test cases")

    print(f"\nTotal test cases: {len(all_cases)}")

    # Connect to KB and find unmatched
    db = KnowledgeDB()
    conn = db._get_conn()

    # Build set of existing (file, function) pairs
    existing = set()
    rows = conn.execute(
        "SELECT test_file, test_function FROM current_tests "
        "WHERE test_file IS NOT NULL AND test_file <> '' "
        "AND test_function IS NOT NULL AND test_function <> ''"
    ).fetchall()
    for r in rows:
        existing.add((r["test_file"], r["test_function"]))
    print(f"Existing KB (file, function) pairs: {len(existing)}")

    # Find unmatched
    unmatched = []
    seen = set()
    for case in all_cases:
        key = (case["file"], case["function"])
        if key in existing or key in seen:
            continue
        if not case["file"] or not case["function"]:
            continue
        seen.add(key)
        unmatched.append(case)

    print(f"Unmatched (need KB artifacts): {len(unmatched)}")

    if dry_run:
        print("\n[DRY RUN] Would create these artifacts:")
        for i, case in enumerate(unmatched[:20]):
            print(f"  {case['file']}::{case['function']} ({case['result']})")
        if len(unmatched) > 20:
            print(f"  ... and {len(unmatched) - 20} more")
        db.close()
        return

    # Get max TEST-NNNN number
    max_num = (
        conn.execute("SELECT MAX(CAST(SUBSTR(id, 6) AS INTEGER)) as n FROM tests WHERE id LIKE 'TEST-%'").fetchone()[
            "n"
        ]
        or 0
    )
    print(f"Starting from TEST-{max_num + 1}")

    now = datetime.now(timezone.utc).isoformat()
    created = 0
    errors = 0

    for case in unmatched:
        max_num += 1
        test_id = f"TEST-{max_num}"
        title = humanize_test_name(case["function"])
        test_type = get_test_type(case["file"])
        spec_id = get_spec_id(case["file"])

        try:
            db.insert_test(
                id=test_id,
                title=title,
                spec_id=spec_id,
                test_type=test_type,
                expected_outcome="pass",
                changed_by="claude",
                change_reason="S147 batch: auto-created from pytest JUnit XML for traceability",
                test_file=case["file"],
                test_class=case["class"],
                test_function=case["function"],
                description=f"Auto-generated from {case['file']}::{case['function']}",
                last_result=case["result"],
                last_executed_at=now,
            )
            created += 1
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ERROR creating {test_id}: {e}")

    print(f"\nCreated: {created}")
    print(f"Errors: {errors}")

    # Check new traceability
    total = conn.execute("SELECT COUNT(DISTINCT id) as c FROM tests").fetchone()["c"]
    traced = conn.execute("SELECT COUNT(*) as c FROM current_tests WHERE last_result IS NOT NULL").fetchone()["c"]
    print(f"\nTest Traceability: {traced}/{total} ({100 * traced / total:.1f}%)")

    db.close()


if __name__ == "__main__":
    main()
